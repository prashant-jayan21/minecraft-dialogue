package cwc;

import com.microsoft.Malmo.Client.MalmoModClient;
import com.microsoft.Malmo.MalmoMod;
import com.microsoft.Malmo.MissionHandlers.AbsoluteMovementCommandsImplementation;
import net.minecraft.client.Minecraft;
import net.minecraft.client.entity.EntityPlayerSP;
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
import net.minecraft.world.GameType;
import net.minecraftforge.client.event.ClientChatReceivedEvent;
import net.minecraftforge.client.event.MouseEvent;
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
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

/**
 * Event handler for CwC mod. Catches some events as they are triggered and modifies vanilla Minecraft behavior.
 * @author nrynchn2
 */
public class CwCEventHandler {

    // used for resetting the Architect to free-fly inspection
    public static boolean reset = false;
    private static boolean unpressed = true;

    // used to handle screenshot logic
    private static boolean receivedChat = false, renderedChat = false;  // chat is received & rendered
    protected static boolean placedBlock = false, pickedUpBlock = false, renderedBlock = false;  // block is placed/picked up & rendered
    protected static boolean updatePlayerTick = false, updateRenderTick = false;  // wait for the second update/render tick of a pickup action before taking a screenshot
    protected static boolean disablePutdown = false, disablePickup = false;  // disallow Builder to putdown/pickup until a screenshot of the last action has been taken

    /**
     * Fired when an entity joins the world (spawns). See {@link EntityJoinWorldEvent} for more details.
     * This piece of code implements multiple features:
     * (1) Only allows players, falling blocks, and items to spawn.
     * (2) Allows the players to fly and be immune to damage.
     * (3) Initializes the Architect with an empty inventory.
     * (4) If the Builder has an empty inventory and is allowed unlimited inventory, initialize it with default stack sizes of all colored blocks.
     *     Otherwise, if the Builder is not allowed unlimited inventory, initialize the Builder with an empty inventory.
     *     If possible, the Builder is initialized with an empty hand.
     *
     * @param event
     */
    @SubscribeEvent
    public void onEntitySpawn(EntityJoinWorldEvent event) {
        // only allow players, falling blocks, and items to spawn
        if (!(event.getEntity() instanceof EntityPlayer || event.getEntity() instanceof EntityFallingBlock || event.getEntity() instanceof EntityItem))
            event.setCanceled(true);

        if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer) {
            EntityPlayerMP player = (EntityPlayerMP) event.getEntity();
            System.out.println("onEntitySpawn: " + player.getName());

            // enable flying and damage immunity
            player.capabilities.allowFlying = true;
            player.capabilities.disableDamage = true;
            player.sendPlayerAbilities();
            System.out.println("\t-- flying capabilities ON, damage OFF");

            // spawn with empty hand (if possible)
            int es = player.inventory.getFirstEmptyStack();
            player.inventory.currentItem = es < 0 ? 0 : es;
            player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));

            // initialize Architect, Oracle, Builder (if limited inventory) with empty inventory
            if (player.getName().equals(MalmoMod.ARCHITECT) || player.getName().equals(MalmoMod.ORACLE) ||
                    (player.getName().equals(MalmoMod.BUILDER) && !CwCMod.unlimitedInventory)) {
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
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.red, CwCMod.DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.orange, CwCMod.DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.yellow, CwCMod.DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.green, CwCMod.DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.blue, CwCMod.DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.purple, CwCMod.DEFAULT_STACK_SIZE));
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
        if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer) {
            EntityPlayerMP player = (EntityPlayerMP) event.getEntityPlayer();
            System.out.println("onPlayerClone: " + player.getName());

            // enable flying and damage immunity
            player.capabilities.allowFlying = true;
            player.capabilities.disableDamage = true;
            player.sendPlayerAbilities();
            System.out.println("\t-- flying capabilities ON, damage OFF");

            // spawn with empty hand (if possible)
            int es = player.inventory.getFirstEmptyStack();
            player.inventory.currentItem = es < 0 ? 0 : es;
            player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));
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
        Minecraft minecraft = Minecraft.getMinecraft();
        GameSettings gs = minecraft.gameSettings;
        EntityPlayerSP player = minecraft.player;

        // Handles mode-switching logic when the TAB key is pressed by either Architect or Builder.
        if (gs.keyBindPlayerList.isPressed()) {
            System.out.println("Player: " + player.getName() + "\tState: " + CwCMod.state);

            // Architect switches from Inspecting to Thinking mode
            if (player.getName().equals(MalmoMod.ARCHITECT) && minecraft.playerController.getCurrentGameType() == GameType.SPECTATOR && CwCMod.state == CwCState.INSPECTING) {
                CwCMod.network.sendToServer(new CwCStateMessage(CwCState.THINKING));

                // Find the Builder, teleport to his position and attack him (to enable third-person mob-view of Builder)
                EntityPlayer builder = null;
                for (EntityPlayer ep : Minecraft.getMinecraft().world.playerEntities)
                    if (ep.getName().equals(MalmoMod.BUILDER)) builder = ep;

                if (builder != null) {
                    gs.thirdPersonView = 1;
                    CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(builder.posX, builder.posY, builder.posZ, 0, 0, true, true, true, true, true));
                    minecraft.playerController.attackEntity(Minecraft.getMinecraft().player, builder);
                }
            }

            // Builder switches from Building to Inspecting mode
            else if (player.getName().equals(MalmoMod.BUILDER) && CwCMod.state == CwCState.BUILDING)
                CwCMod.network.sendToServer(new CwCStateMessage(CwCState.INSPECTING));

            // Unpress the key
            KeyBinding.unPressAllKeys();
        }

        // Builder keybinds
        else if (player.getName().equals(MalmoMod.BUILDER)) {
            // ignore all keypresses if not in Building mode
            if (CwCMod.state != CwCState.BUILDING) KeyBinding.unPressAllKeys();

            // ignore regular set of keypresses while building (e.g. dropping items, swapping hands, inventory, etc.)
            else if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed());
        }

        // Architect keybinds
        else if (player.getName().equals(MalmoMod.ARCHITECT)) {
            // disable opening chatbox while Inspecting
            if (CwCMod.state == CwCState.INSPECTING && (gs.keyBindChat.isPressed() || gs.keyBindCommand.isPressed()));

            // do not allow Architect to stop Builder mob-view in Thinking, Building modes
            if (CwCMod.state != CwCState.INSPECTING && gs.keyBindSneak.isPressed()) KeyBinding.unPressAllKeys();

            // ignore regular set of keypresses
            if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed());

            // ignore hotbar keypresses (in vanilla Minecraft, this would switch the spectator's choice of mob-view)
            for (KeyBinding kb : gs.keyBindsHotbar) if (kb.isPressed());
        }

        // Oracle keybinds
        else if (player.getName().equals(MalmoMod.ORACLE)) {
            // ignore regular set of keypresses
            if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed());

            // ignore hotbar keypresses (in vanilla Minecraft, this would switch the spectator's choice of mob-view)
            for (KeyBinding kb : gs.keyBindsHotbar) if (kb.isPressed());
        }

    }

    /**
     * Fired when a change of mouse input is detected. See {@link MouseEvent} for more details.
     * Disable Builder's mouse unless in the Building state.
     *
     * @param event
     */
    @SubscribeEvent
    public void onMouseInput(MouseEvent event) {
        EntityPlayer player = Minecraft.getMinecraft().player;
        if (player.getName().equals(MalmoMod.BUILDER) && CwCMod.state != CwCState.BUILDING)
            event.setCanceled(true);
    }

    /**
     * Fired when a living entity is updated via onUpdate(). See {@link net.minecraftforge.event.entity.living.LivingEvent.LivingUpdateEvent} for more details.
     * This piece of code implements multiple features:
     * (1) Prevents noclipping through floor.
     * (2) Resets the Architect from mob-view to free camera when the Builder ends his Building turn by simulating a "sneak" keypress.
     * (3) Initializes the Builder with an overridden mouse (i.e., mouse cannot be clicked, and changes in mouse's location are not registered as mouse movements).
     *     Also handles the mouse override logic for the Builder based on the current mode.
     * (4) Produces the text overlay that displays the current mode for both Architect and Builder.
     * (5) Prompts the Architect and Builder clients to take screenshots when a chat or block action has been executed and rendered.
     *
     * @param event
     */
    @SubscribeEvent
    public void onPlayerUpdate(LivingEvent.LivingUpdateEvent event) {
        EntityPlayer player = (EntityPlayer) event.getEntity();

        // prevent noclip through floor
        if (player.posY < 0) {
            event.setCanceled(true);
            player.setPositionAndUpdate(player.posX, 0, player.posZ);
        }

        if (player.getEntityWorld().isRemote) {
            Minecraft minecraft = Minecraft.getMinecraft();
            if (player.getName().equals(MalmoMod.ARCHITECT)) {

                // when resetting to Inspecting mode, press the 'sneak' key and set Architect back to first-person view
                if (CwCMod.state == CwCState.INSPECTING && reset) {
                    KeyBinding.setKeyBindState(Minecraft.getMinecraft().gameSettings.keyBindSneak.getKeyCode(), true);
                    Minecraft.getMinecraft().gameSettings.thirdPersonView = 0;
                    reset = false;
                    unpressed = false;
                }

                // unpress the 'sneak' key & teleport behind (and slightly above) Builder's current position
                else if (Minecraft.getMinecraft().gameSettings.keyBindSneak.isKeyDown() && !unpressed) {
                    KeyBinding.unPressAllKeys();
                    unpressed = true;

                    EntityPlayer builder = null;
                    for (EntityPlayer ep : Minecraft.getMinecraft().world.playerEntities)
                        if (ep.getName().equals(MalmoMod.BUILDER)) builder = ep;

                    if (builder != null)
                        CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(builder.posX, builder.posY + 3, builder.posZ - 3, 0, 45, true, true, true, true, true));
                }

                // set mode overlay message for Architect
                if (minecraft.player.getName().equals(MalmoMod.ARCHITECT))
                    minecraft.ingameGUI.setOverlayMessage(CwCUtils.statusOverlay[CwCMod.state.ordinal()], true);

            }

            // set mode overlay message for Builder
            else if (player.getName().equals(MalmoMod.BUILDER) && minecraft.player.getName().equals(MalmoMod.BUILDER)) {
                minecraft.ingameGUI.setOverlayMessage(CwCUtils.statusOverlay[CwCMod.state.ordinal()], true);

                // if switching from Building to Inspecting and mouse hasn't yet been overridden, override the mouse
                if (CwCMod.state != CwCState.BUILDING && minecraft.mouseHelper instanceof MalmoModClient.MouseHook &&
                        !((MalmoModClient.MouseHook) minecraft.mouseHelper).isOverriding)
                    ((MalmoModClient.MouseHook) minecraft.mouseHelper).isOverriding = true;
            }

            // take a screenshot when a chat message has been received and rendered by the client
            if (receivedChat && renderedChat) {
                System.out.println("Chat received & rendered: taking screenshot...");
                CwCUtils.takeScreenshot(Minecraft.getMinecraft(), CwCUtils.useTimestamps, CwCScreenshotEventType.CHAT);
                receivedChat = false;
                renderedChat = false;
            }

            // take a screenshot when a block place event has been received and rendered by the client
            if (placedBlock && renderedBlock) {
                System.out.println("Block placed & rendered: taking screenshot...");
                CwCUtils.takeScreenshot(Minecraft.getMinecraft(), CwCUtils.useTimestamps, CwCScreenshotEventType.PUTDOWN);
                placedBlock = false;
                renderedBlock = false;
            }

            // when a block is broken, force to wait for another tick of player update + rendering before taking the screenshot
            if (pickedUpBlock && renderedBlock && !updatePlayerTick) updatePlayerTick = true;

            // take a screenshot when a block break event has been received and rendered by the client
            else if (pickedUpBlock && renderedBlock && updatePlayerTick && updateRenderTick) {
                System.out.println("Block removed, picked up & rendered: taking screenshot...");
                CwCUtils.takeScreenshot(Minecraft.getMinecraft(), CwCUtils.useTimestamps, CwCScreenshotEventType.PICKUP);
                pickedUpBlock = false;
                renderedBlock = false;
                updatePlayerTick = false;
                updateRenderTick = false;
            }
        }

        //TODO: calculations of visible entities
//        if (player.getEntityWorld().isRemote) {
//            ICamera icamera = new Frustum();
//            Entity entity = Minecraft.getMinecraft().getRenderViewEntity();;
//            icamera.setPosition(entity.lastTickPosX, entity.lastTickPosY, entity.lastTickPosZ);
//        }
    }

    /**
     * Fired when the game overlay is rendered for a client. See {@link RenderGameOverlayEvent} for more details.
     * Hides health, hunger, and experience bars. Also hides the hotbar for the Architect and Oracle spectators.
     * Also helps manage logic for taking screenshots after an action has been rendered.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void renderGameOverlay(RenderGameOverlayEvent event) {
        if (event.getType().equals(ElementType.HEALTH) || event.getType().equals(ElementType.FOOD) || event.getType().equals(ElementType.EXPERIENCE))
            event.setCanceled(true);

        Minecraft minecraft = Minecraft.getMinecraft();
        if ((minecraft.player.getName().equals(MalmoMod.ARCHITECT) || minecraft.player.getName().equals(MalmoMod.ORACLE)) && event.getType().equals(ElementType.HOTBAR))
            event.setCanceled(true);

        // register the rendering of an action after player update
        if (placedBlock || pickedUpBlock) renderedBlock = true;

        // second render tick after the second player update tick
        if (pickedUpBlock && renderedBlock && updatePlayerTick) updateRenderTick = true;
    }

    /**
     * Fired when a chat message is received on the client. See {@link ClientChatReceivedEvent} for more details.
     * Immediately switches to Building mode upon receiving the first utterance from the Architect in Thinking mode.
     * Sets boolean field indicating a screenshot should be taken once the chat message has been rendered.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onClientChatReceived(ClientChatReceivedEvent event) {
        Minecraft minecraft = Minecraft.getMinecraft();
        EntityPlayer player = minecraft.player;

        // switch to Building mode upon first Architect utterance in Thinking mode
        if (player.getName().equals(MalmoMod.ARCHITECT) && minecraft.playerController.getCurrentGameType() == GameType.SPECTATOR && CwCMod.state == CwCState.THINKING)
            CwCMod.network.sendToServer(new CwCStateMessage(CwCState.BUILDING));

        // take a screenshot if message is non-system message
        if (event.getType() == 0) receivedChat = true;
    }

    /**
     * Fired when a chat message is rendered on the client. See {@link net.minecraftforge.client.event.RenderGameOverlayEvent.Chat} for more details.
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
        if (event.getEntity() instanceof EntityPlayer && event.getEntity().getName().equals(MalmoMod.BUILDER) &&
                CwCMod.state == CwCState.BUILDING) {
            EntityPlayer player = (EntityPlayer) event.getEntity();

            // count the number of items currently in his inventory (hotbar)
            int items = 0;
            for (int i = 0; i < InventoryPlayer.getHotbarSize(); i++)
                items += player.inventory.getStackInSlot(i).getCount();

            // cancel the left-click event if Builder is not allowed to pick up any more blocks at this time
            if ((!CwCMod.unlimitedInventory && items >= CwCMod.MAX_INVENTORY_SIZE) || disablePickup) event.setCanceled(true);
        }
    }

    /**
     * Fired when a block is placed by a player. See {@link net.minecraftforge.event.world.BlockEvent.PlaceEvent} for more details.
     * Sets held item to first empty slot upon placing a block.
     * If, for some reason, no hotbar slots are empty, then this does nothing.
     * Also starts the process for taking a screenshot (on both clients) upon placing blocks.
     *
     * @param event
     */
    @SubscribeEvent
    public void onBlockPlace(BlockEvent.PlaceEvent event) {
        if (!event.getPlayer().getEntityWorld().isRemote && event.getPlayer() instanceof EntityPlayerMP) {
            EntityPlayerMP player = (EntityPlayerMP) event.getPlayer();
            System.out.println("Block " + event.getPlacedBlock().getBlock().getUnlocalizedName() + " placed by " + player.getName());

            // find first empty slot in the hotbar and set the held item to it (if possible)
            int empty = player.inventory.getFirstEmptyStack();
            player.inventory.currentItem = empty < 0 ? player.inventory.currentItem : empty;

            // let the server know that the held item has been changed
            // (and also notify in order to prepare to take a screenshot)
            player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));
            CwCMod.network.sendToServer(new CwCScreenshotMessage(CwCScreenshotEventType.PUTDOWN));

            // don't allow any more blocks to be placed until the screenshot has been taken
            disablePutdown = true;
        }
    }

    /**
     * Fired when a block is broken by an entity. See {@link net.minecraftforge.event.world.BlockEvent.BreakEvent} for more details.
     * Does not allow player to break any further blocks until a screenshot of the last break event has been taken.
     * @param event
     */
    @SubscribeEvent
    public void onBlockBreak(BlockEvent.BreakEvent event) { disablePickup = true; }

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
            System.out.println("Item " + event.getItem().getName() + " picked up by " + player.getName());

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
    public void playerFall(LivingFallEvent event) { if (event.getEntity() instanceof EntityPlayer) event.setDistance(0.0F); }
}
