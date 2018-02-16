package cwc;

import com.microsoft.Malmo.MissionHandlers.AbsoluteMovementCommandsImplementation;
import net.minecraft.client.Minecraft;
import net.minecraft.client.entity.EntityPlayerSP;
import net.minecraft.client.gui.GuiChat;
import net.minecraft.client.settings.GameSettings;
import net.minecraft.client.settings.KeyBinding;
import net.minecraft.entity.item.EntityFallingBlock;
import net.minecraft.entity.item.EntityItem;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.entity.player.InventoryPlayer;
import net.minecraft.init.Items;
import net.minecraft.item.ItemStack;
import net.minecraft.network.play.server.SPacketHeldItemChange;
import net.minecraftforge.client.event.ClientChatReceivedEvent;
import net.minecraftforge.client.event.RenderGameOverlayEvent;
import net.minecraftforge.client.event.RenderGameOverlayEvent.ElementType;
import net.minecraftforge.event.entity.EntityJoinWorldEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingFallEvent;
import net.minecraftforge.event.entity.player.EntityItemPickupEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.world.BlockEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.InputEvent.*;
import net.minecraftforge.fml.common.gameevent.TickEvent;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

import java.util.List;

import static cwc.CwCUtils.playerNameMatches;
import static cwc.CwCUtils.playerNameMatchesAny;

/**
 * Event handler for CwC mod. Catches some events as they are triggered and modifies vanilla Minecraft behavior.
 *
 * @author nrynchn2
 */
public class CwCEventHandler {

    // mission quit
    protected static boolean quit = false;

    // initialization indicators for server and client
    protected static boolean initializedTimestamp = false;

    // indicates whether the current player or their dialogue partner is chatting
    protected static boolean chatting = false;
    protected static boolean partnerIsChatting = false;

    // for screenshot logic
    private static boolean receivedChat = false, renderedChat = false;            // chat is received & rendered
    private static int sentChatMessages = 0;                                      // number of chat messages sent (by Architect)
    protected static boolean placedBlock = false, pickedUpBlock = false;          // block is placed or picked up
    private static boolean renderedBlock = false;                                 // block is rendered
    private static boolean updatePlayerTick = false, updateRenderTick = false;    // wait for the second update/render tick of a pickup action before taking a screenshot
    protected static boolean disablePutdown = false, disablePickup = false;       // disallows Builder to putdown/pickup until a screenshot of the last action has been taken

    // for Architect follow logic
    private static boolean following = false, sneaking = false;  // resets the architect's position after his chat box is closed
    protected static double builderCurrentY = Double.MIN_VALUE;  // keeps track of Builder's current Y-value

    /**
     * Resets the necessary boolean fields.
     */
    protected static void reset() {
        resetInitializationFields();
        resetChatInitializationFields();
        resetChatScreenshotFields();
        resetArchitectFollowFields();
        resetPlaceBlockFields();
        resetBreakBlockFields();
    }

    /**
     * Fired when an entity joins the world (spawns). See {@link EntityJoinWorldEvent} for more details.
     * This piece of code implements multiple features:
     * (1) Only allows players, falling blocks, and items to spawn.
     * (2) Allows the players to fly and be immune to damage.
     * (3) Initializes the Architect with an empty inventory.
     * (4) If the Builder has an empty inventory and is allowed unlimited inventory, initialize it with default stack sizes of all colored blocks.
     * Otherwise, if the Builder is not allowed unlimited inventory, initialize the Builder with an empty inventory.
     * If possible, the Builder is initialized with an empty hand.
     *
     * @param event
     */
    @SubscribeEvent
    public void onEntitySpawn(EntityJoinWorldEvent event) {
        // only allow players, falling blocks, and items to spawn
        if (!(event.getEntity() instanceof EntityPlayer || event.getEntity() instanceof EntityFallingBlock || event.getEntity() instanceof EntityItem))
            event.setCanceled(true);

        if (event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer)
            resetGameSettingsAndChatGUI();

        else if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer) {
            EntityPlayerMP player = (EntityPlayerMP) event.getEntity();
            System.out.println("onEntitySpawn: " + player.getName());

            // enable flying and damage immunity
            player.capabilities.allowFlying = true;
            player.capabilities.disableDamage = true;
            player.sendPlayerAbilities();
            System.out.println("\t-- flying capabilities ON, damage OFF");

            // spawn with empty hand (if possible)
            if (playerNameMatches(player, CwCMod.BUILDER)) {
                int es = player.inventory.getFirstEmptyStack();
                player.inventory.currentItem = es < 0 ? 0 : es;
                player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));
            }

            // initialize Architect, Builder (if limited inventory) with empty inventory
            if (playerNameMatches(player, CwCMod.ARCHITECT) || playerNameMatches(player, CwCMod.ORACLE) || playerNameMatchesAny(player, CwCMod.FIXED_VIEWERS) ||
                    (playerNameMatches(player, CwCMod.BUILDER) && !CwCMod.unlimitedInventory)) {
                for (int i = 0; i < InventoryPlayer.getHotbarSize(); i++)
                    player.inventory.setInventorySlotContents(i, ItemStack.EMPTY);
                return;
            }

            // unlimited inventory: check for empty inventory
            boolean empty = true;
            for (int i = 0; i < InventoryPlayer.getHotbarSize(); i++) {
                if (!player.inventory.getStackInSlot(i).isEmpty()) {
                    empty = false;
                    break;
                }
            }

            // unlimited inventory: initialize the inventory with default stack sizes
            if (empty) {
                for (CwCBlock block : StartupCommon.blocks)
                    player.inventory.addItemStackToInventory(new ItemStack(block, CwCMod.DEFAULT_STACK_SIZE));
                System.out.println("\t-- inventory INITIALIZED");
            }
        }
    }

    /**
     * Fired when an entity respawns (e.g., after they are killed). See {@link net.minecraftforge.event.entity.player.PlayerEvent.Clone} for more details.
     * Re-enables flying and damage immunity should the player respawn, and also respawns him with an empty hand.
     *
     * @param event
     */
    @SubscribeEvent
    public void onPlayerClone(PlayerEvent.Clone event) {
        if (event.getEntity().getEntityWorld().isRemote  && event.getEntity() instanceof EntityPlayer)
            resetGameSettingsAndChatGUI();

        else if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer) {
            EntityPlayerMP player = (EntityPlayerMP) event.getEntityPlayer();
            System.out.println("onPlayerClone: " + player.getName());

            // enable flying and damage immunity
            player.capabilities.allowFlying = true;
            player.capabilities.disableDamage = true;
            player.sendPlayerAbilities();
            System.out.println("\t-- flying capabilities ON, damage OFF");

            // spawn with empty hand (if possible)
            if (playerNameMatches(player, CwCMod.BUILDER)) {
                int es = player.inventory.getFirstEmptyStack();
                player.inventory.currentItem = es < 0 ? 0 : es;
                player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));
            }
        }
    }

    /**
     * Fired when any key is pressed. See {@link KeyInputEvent} for more details.
     * Handles all keybinds. Tab switches modes from Inspecting to Thinking & Building to Inspecting. Some subset of
     * keybinds are disabled for players based on the current mode.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onKeyInput(KeyInputEvent event) {
        Minecraft mc = Minecraft.getMinecraft();
        GameSettings gs = mc.gameSettings;
        EntityPlayerSP player = mc.player;

        // Builder keybinds
        if (playerNameMatches(player, CwCMod.BUILDER)) {
            // ignore regular set of keypresses while building (e.g. dropping items, swapping hands, inventory, etc.)
            if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed()) ;
        }

        // Architect keybinds
        else if (playerNameMatches(player, CwCMod.ARCHITECT)) {
            // assume third-person mob-view of Builder when initiating a chat
            if (gs.keyBindChat.isPressed()) {
                EntityPlayer builder = null;
                for (EntityPlayer ep : mc.world.playerEntities)
                    if (playerNameMatches(ep, CwCMod.BUILDER)) builder = ep;

                CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(builder.posX, builder.posY, builder.posZ, 0, 0, true, true, true, true, true));
                mc.playerController.attackEntity(Minecraft.getMinecraft().player, builder);
                mc.displayGuiScreen(new GuiChat());
                gs.thirdPersonView = 1;
                following = true;
            }

            // ignore regular set of keypresses
            if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed()) ;

            // ignore hotbar keypresses (in vanilla Minecraft, this would switch the spectator's choice of mob-view)
            for (KeyBinding kb : gs.keyBindsHotbar) if (kb.isPressed()) ;
        }

        else if (playerNameMatches(player, CwCMod.ORACLE)) {
            // ignore regular set of keypresses while building (e.g. dropping items, swapping hands, inventory, etc.)
            if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed() || gs.keyBindChat.isPressed()) ;
        }

        else if (playerNameMatchesAny(player, CwCMod.FIXED_VIEWERS)) {
            // ignore regular set of keypresses while building (e.g. dropping items, swapping hands, inventory, etc.) and disable movement
            if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed() || gs.keyBindChat.isPressed() ||
                    gs.keyBindForward.isPressed() || gs.keyBindBack.isPressed() || gs.keyBindLeft.isPressed() || gs.keyBindRight.isPressed() ||
                    gs.keyBindJump.isPressed() || gs.keyBindSneak.isPressed()) ;

            if (gs.keyBindForward.isKeyDown() || gs.keyBindBack.isKeyDown() || gs.keyBindLeft.isKeyDown() || gs.keyBindRight.isKeyDown() ||
                    gs.keyBindJump.isKeyDown() || gs.keyBindSneak.isKeyDown())
                KeyBinding.unPressAllKeys();
        }
    }

    /**
     * Fired when a client ticks. See {@link net.minecraftforge.fml.common.gameevent.TickEvent.ClientTickEvent} for more details.
     * Quits the mission (kills all connected players) when the Ctrl+C key combination is pressed.
     * Also starts the process to exit Architect's mob-view when his chat window is closed.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onClientTick(TickEvent.ClientTickEvent event) {
        if (quit) return;

        Minecraft mc = Minecraft.getMinecraft();

        // Quits the mission if Ctrl-C is pressed by either player, killing all connected players.
        if ((CwCKeybinds.quitKeyC.isKeyDown() && CwCKeybinds.quitCtrl.isKeyDown() &&
                (playerNameMatches(mc, CwCMod.ARCHITECT) || playerNameMatches(mc, CwCMod.BUILDER))) ||
                (CwCKeybinds.quitKeyQ.isKeyDown() && CwCKeybinds.quitCtrl.isKeyDown() &&
                (playerNameMatches(mc, CwCMod.ORACLE) || playerNameMatchesAny(mc, CwCMod.FIXED_VIEWERS)))) {
            System.out.println("CwCMod: Quitting the mission...");
            CwCMod.network.sendToServer(new CwCQuitMessage());
            // Unpress the keys
            KeyBinding.unPressAllKeys();
        }

        // exit mob-view when chat window is closed
        if (mc != null && mc.player != null && playerNameMatches(mc, CwCMod.ARCHITECT)) {
            if (mc.ingameGUI.getChatGUI().getSentMessages().size() > sentChatMessages) {
                CwCUtils.takeScreenshot(mc, CwCUtils.useTimestamps, CwCScreenshotEventType.CHAT);
                sentChatMessages = mc.ingameGUI.getChatGUI().getSentMessages().size();
                resetChatScreenshotFields();
            }

            if (following && !mc.ingameGUI.getChatGUI().getChatOpen()) {
                KeyBinding.setKeyBindState(mc.gameSettings.keyBindSneak.getKeyCode(), true);
                mc.gameSettings.thirdPersonView = 0;
                sneaking = true;
            }
        }

        if (mc != null && mc.player != null) {
            if (!chatting && mc.ingameGUI.getChatGUI().getChatOpen()) {
                CwCMod.network.sendToServer(new CwCChatMessage(true));
                chatting = true;
            } else if (chatting && !mc.ingameGUI.getChatGUI().getChatOpen()) {
                CwCMod.network.sendToServer(new CwCChatMessage(false));
                chatting = false;
            }
        }

        if (partnerIsChatting && !playerNameMatchesAny(mc, CwCMod.FIXED_VIEWERS)) {
            String partner = playerNameMatches(mc, CwCMod.ARCHITECT) ? "Builder" : "Architect";
            mc.ingameGUI.setOverlayMessage(partner + " is typing...", true);
        } else mc.ingameGUI.setOverlayMessage("", false);
    }

    /**
     * Fired when a living entity is updated via onUpdate(). See {@link net.minecraftforge.event.entity.living.LivingEvent.LivingUpdateEvent} for more details.
     * This piece of code implements multiple features:
     * (1) Prevents noclipping through floor.
     * (2) Continues to reset the Architect from mob-view to free camera by simulating a "sneak" keypress, which is initiated in {@link #onClientTick(TickEvent.ClientTickEvent)}.
     * (3) Prompts the Architect and Builder clients to take screenshots when a chat or block action has been executed and rendered.
     *
     * @param event
     */
    @SubscribeEvent
    public void onPlayerUpdate(LivingEvent.LivingUpdateEvent event) {
        if (quit) return;

        EntityPlayer updatedPlayer = (EntityPlayer) event.getEntity();

        // prevent noclip through floor
        if (updatedPlayer.posY < 0) {
            event.setCanceled(true);
            updatedPlayer.setPositionAndUpdate(updatedPlayer.posX, 0, updatedPlayer.posZ);
        }

        if (updatedPlayer.getEntityWorld().isRemote) {
            Minecraft mc = Minecraft.getMinecraft();
            EntityPlayer player = mc.player;

            // Architect sneaking to break mob-view
            if (playerNameMatches(player, CwCMod.ARCHITECT) && sneaking) {
                CwCMod.network.sendToServer(new CwCPositionMessage());

                // once the Architect's y-coordinate position differs from the Builder's, teleport him to a neutral position
                if (player.posY < builderCurrentY - 0.1) {
                    KeyBinding.unPressAllKeys();
                    CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(0, 5, -5, 0, 45, true, true, true, true, true));
                    resetArchitectFollowFields();
                }
            }

            // take a screenshot when a chat message has been received and rendered by the client
            if (receivedChat && renderedChat) {
                if (!playerNameMatchesAny(player, CwCMod.FIXED_VIEWERS) ||
                        (playerNameMatchesAny(player, CwCMod.FIXED_VIEWERS) && !initializedTimestamp))
                    CwCUtils.takeScreenshot(mc, CwCUtils.useTimestamps, CwCScreenshotEventType.CHAT);
                resetChatScreenshotFields();
            }

            // take a screenshot when a block place event has been received and rendered by the client
            if (placedBlock && renderedBlock) {
                CwCUtils.takeScreenshot(mc, CwCUtils.useTimestamps, CwCScreenshotEventType.PUTDOWN);
                resetPlaceBlockFields();
            }

            // when a block is broken, force to wait for another tick of player update + rendering before taking the screenshot
            if (pickedUpBlock && renderedBlock && !updatePlayerTick) updatePlayerTick = true;

                // take a screenshot when a block break event has been received and rendered by the client
            else if (pickedUpBlock && renderedBlock && updatePlayerTick && updateRenderTick) {
                CwCUtils.takeScreenshot(mc, CwCUtils.useTimestamps, CwCScreenshotEventType.PICKUP);
                resetBreakBlockFields();
            }
        }
    }

    /**
     * Fired when the game overlay is rendered for a client. See {@link RenderGameOverlayEvent} for more details.
     * Hides health, hunger, and experience bars. Also hides the hotbar for the Architect.
     * Also helps manage logic for taking screenshots after an action has been rendered.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void renderGameOverlay(RenderGameOverlayEvent event) {
        if (event.getType().equals(ElementType.HEALTH) || event.getType().equals(ElementType.FOOD) || event.getType().equals(ElementType.EXPERIENCE))
            event.setCanceled(true);

        // register the rendering of an action after player update
        if (placedBlock || pickedUpBlock) renderedBlock = true;

        // second render tick after the second player update tick
        if (pickedUpBlock && renderedBlock && updatePlayerTick) updateRenderTick = true;
    }

    /**
     * Fired when a chat message is received on the client. See {@link ClientChatReceivedEvent} for more details.
     * Sets boolean field indicating a screenshot should be taken once the chat message has been rendered.
     * For the Architect, this is calculated by checking the number of sent messages by the Architect player and comparing
     * it to the last known number, triggering a screenshot slightly before the chat message
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onClientChatReceived(ClientChatReceivedEvent event) {
        Minecraft mc = Minecraft.getMinecraft();
        EntityPlayer player = mc.player;

        // take a screenshot if message is non-system message
        if (event.getType() == 0) {
            List<String> sentMessages = mc.ingameGUI.getChatGUI().getSentMessages();
            if (playerNameMatches(player, CwCMod.BUILDER) || playerNameMatchesAny(player, CwCMod.FIXED_VIEWERS) ||
                    (playerNameMatches(player, CwCMod.ARCHITECT) && (sentMessages.size() == 0 ||
                    sentMessages.size() > 0 && !event.getMessage().getUnformattedText().equals("<Architect> " + sentMessages.get(sentMessages.size() - 1)))))
                receivedChat = true;
        }
    }

    /**
     * Fired when a chat message is rendered on the client. See {@link net.minecraftforge.client.event.RenderGameOverlayEvent.Chat} for more details.
     *
     * @param event
     */
    @SubscribeEvent
    public void onChatRendered(RenderGameOverlayEvent.Chat event) {
        if (receivedChat) renderedChat = true;
    }

    /**
     * Fired when a block is left-clicked by a player. See {@link net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock} for more details.
     * If the Builder has limited inventory and he has already reached the maximum number of allowed items in his inventory, this prevents him from picking up any more items.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onBlockClicked(PlayerInteractEvent.LeftClickBlock event) {
        if (event.getEntity() instanceof EntityPlayer && event.getEntity().getName().equals(CwCMod.BUILDER)) {
            EntityPlayer player = (EntityPlayer) event.getEntity();

            // count the number of items currently in his inventory (hotbar)
            int items = 0;
            for (int i = 0; i < InventoryPlayer.getHotbarSize(); i++)
                items += player.inventory.getStackInSlot(i).getCount();

            // cancel the left-click event if Builder is not allowed to pick up any more blocks at this time
            if ((!CwCMod.unlimitedInventory && items >= CwCMod.MAX_INVENTORY_SIZE) || disablePickup)
                event.setCanceled(true);
        }
    }

    /**
     * Fired when a block is placed by a player. See {@link net.minecraftforge.event.world.BlockEvent.PlaceEvent} for more details.
     * Starts the process for taking a screenshot (on both clients) upon placing blocks.
     * Disables the player from putting down any more blocks until the
     *
     * @param event
     */
    @SubscribeEvent
    public void onBlockPlace(BlockEvent.PlaceEvent event) {
        if (!event.getPlayer().getEntityWorld().isRemote && event.getPlayer() instanceof EntityPlayerMP) {
            CwCMod.network.sendToServer(new CwCScreenshotMessage(CwCScreenshotEventType.PUTDOWN));
            // don't allow any more blocks to be placed until the screenshot has been taken
            disablePutdown = true;
        }
    }

    /**
     * Fired when a block is broken by an entity. See {@link net.minecraftforge.event.world.BlockEvent.BreakEvent} for more details.
     * Does not allow player to break any further blocks until a screenshot of the last break event has been taken.
     *
     * @param event
     */
    @SubscribeEvent
    public void onBlockBreak(BlockEvent.BreakEvent event) {
        disablePickup = true;
    }

    /**
     * Fired when an item is picked up by an entity. See {@link EntityItemPickupEvent} for more details.
     * Switches active hotbar slot to the item just picked up, or first empty slot if the item doesn't exist in hotbar.
     * If, for some reason, the hotbar is full and the item doesn't exist in hotbar already, the currently held item isn't changed.
     * Also starts the process for taking a screenshot (on both clients) upon item pickup.
     *
     * @param event
     */
    @SubscribeEvent
    public void onItemPickup(EntityItemPickupEvent event) {
        if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayerMP) {
            EntityPlayerMP player = (EntityPlayerMP) event.getEntityPlayer();
//            System.out.println("Item " + event.getItem().getName() + " picked up by " + player.getName());

            // Due to how mouseclicks are handled, usually a pickup event is also fired for the player attempting to pick up Air. We will ignore this.
            if (event.getItem().getEntityItem().getItem() != Items.AIR) {
                int slot = player.inventory.getSlotFor(event.getItem().getEntityItem()); // hotbar slot in which this item already exists
                int empty = player.inventory.getFirstEmptyStack();                       // first empty hotbar slot

                // switch to item hotbar slot if it exists; otherwise, switch to first empty slot if it exists; otherwise, do nothing
                player.inventory.currentItem = InventoryPlayer.isHotbar(slot) ? slot : empty < 0 ? player.inventory.currentItem : empty;

                // let the server know that the held item has been changed
                // (and also notify server to inform clients to prepare to take a screenshot)
                player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));
                CwCMod.network.sendToServer(new CwCScreenshotMessage(CwCScreenshotEventType.PICKUP));
            }
        }
    }

    /**
     * Fired when a living entity falls. See {@link LivingFallEvent} for more details.
     * Disables falling damage.
     *
     * @param event
     */
    @SubscribeEvent
    public void playerFall(LivingFallEvent event) {
        if (event.getEntity() instanceof EntityPlayer) event.setDistance(0.0F);
    }

    /**
     * Helper: reset the boolean fields associated with receiving and rendering chat.
     */
    private static void resetChatScreenshotFields() {
        receivedChat = false;
        renderedChat = false;
    }

    private static void resetChatInitializationFields() {
        sentChatMessages = 0;
        chatting = false;
        partnerIsChatting = false;
    }

    /**
     * Helper: reset the boolean fields associated with placing a block.
     */
    private static void resetPlaceBlockFields() {
        placedBlock = false;
        renderedBlock = false;
        disablePutdown = false;
    }

    /**
     * Helper: reset the boolean fields associated with breaking a block.
     */
    private static void resetBreakBlockFields() {
        pickedUpBlock = false;
        renderedBlock = false;
        updatePlayerTick = false;
        updateRenderTick = false;
        disablePickup = false;
    }

    /**
     * Helper: reset the boolean fields associated with Architect's mob-view.
     */
    private static void resetArchitectFollowFields() {
        following = false;
        sneaking = false;
        builderCurrentY = Double.MIN_VALUE;
    }

    private static void resetInitializationFields() {
        quit = false;
        initializedTimestamp = false;
    }

    private static void resetGameSettingsAndChatGUI() {
        System.out.println("Resetting the chat GUI.");
        Minecraft mc = Minecraft.getMinecraft();
        GameSettings gs = mc.gameSettings;
        gs.thirdPersonView = 0;
        gs.chatVisibility = EntityPlayer.EnumChatVisibility.FULL;
        mc.ingameGUI.getChatGUI().clearChatMessages(true);
    }
}
