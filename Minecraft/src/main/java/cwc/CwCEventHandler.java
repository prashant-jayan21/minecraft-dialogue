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
import net.minecraftforge.event.world.BlockEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.InputEvent.*;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

public class CwCEventHandler {

    public static boolean reset = false;                // used for resetting the Architect to free-fly inspection
    private static boolean unpressed = true;            // used for resetting the Architect to free-fly inspection
    private static int DEFAULT_STACK_SIZE = 50;

    /**
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onKeyInput(KeyInputEvent event) {
        Minecraft minecraft = Minecraft.getMinecraft();
        GameSettings gs = minecraft.gameSettings;
        EntityPlayerSP player = minecraft.player;

        // Handles turn-switching logic when the TAB key is pressed by either Architect or Builder.
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
            if (CwCMod.state != CwCState.INSPECTING && gs.keyBindSneak.isPressed()) KeyBinding.unPressAllKeys();
            if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed());
            for (KeyBinding kb : gs.keyBindsHotbar) if (kb.isPressed());
        }

        else if (player.getName().equals(MalmoMod.ORACLE)) {
            //TODO: also disable attacking/interacting here!
            if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                    gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                    gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() ||
                    gs.keyBindSpectatorOutlines.isPressed());
            for (KeyBinding kb : gs.keyBindsHotbar) if (kb.isPressed());
        }

    }


    /**
     * Disable Builder's mouse unless in the Building state.
     * @param event
     */
    @SubscribeEvent
    public void onMouseInput(MouseEvent event) {
        if (Minecraft.getMinecraft().player.getName().equals(MalmoMod.BUILDER) && CwCMod.state != CwCState.BUILDING)
            event.setCanceled(true);
    }

    /**
     * Prevents noclipping through floor.
     * Resets the Architect from mob-view to free camera when the Builder ends his Building turn by simulating a "sneak" keypress.
     * Initializes Builder with an overridden mouse.
     *
     * @param event
     */
    @SubscribeEvent
    public void onPlayerUpdate(LivingEvent.LivingUpdateEvent event) {
        EntityPlayer player = (EntityPlayer) event.getEntity();
        if (player.posY < 0) {
            event.setCanceled(true);
            player.setPositionAndUpdate(player.posX, 0, player.posZ);
        }

        if (player.getEntityWorld().isRemote) {
            Minecraft minecraft = Minecraft.getMinecraft();
            if (player.getName().equals(MalmoMod.ARCHITECT)) {
                if (CwCMod.state == CwCState.INSPECTING && reset) {
                    KeyBinding.setKeyBindState(Minecraft.getMinecraft().gameSettings.keyBindSneak.getKeyCode(), true);
                    Minecraft.getMinecraft().gameSettings.thirdPersonView = 0;
                    reset = false;
                    unpressed = false;
                } else if (Minecraft.getMinecraft().gameSettings.keyBindSneak.isKeyDown() && !unpressed) {
                    KeyBinding.unPressAllKeys();
                    unpressed = true;

                    EntityPlayer builder = null;
                    for (EntityPlayer ep : Minecraft.getMinecraft().world.playerEntities)
                        if (ep.getName().equals(MalmoMod.BUILDER)) builder = ep;

                    if (builder != null)
                        CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(builder.posX, builder.posY + 3, builder.posZ - 3, 0, 45, true, true, true, true, true));
                }

                if (minecraft.player.getName().equals(MalmoMod.ARCHITECT))
                    minecraft.ingameGUI.setOverlayMessage(CwCUtils.statusOverlay[CwCMod.state.ordinal()], false);

            } else if (player.getName().equals(MalmoMod.BUILDER) && minecraft.player.getName().equals(MalmoMod.BUILDER)) {
                minecraft.ingameGUI.setOverlayMessage(CwCUtils.statusOverlay[CwCMod.state.ordinal()], false);

                if (CwCMod.state != CwCState.BUILDING && minecraft.mouseHelper instanceof MalmoModClient.MouseHook &&
                        ((MalmoModClient.MouseHook) minecraft.mouseHelper).isOverriding == false)
                    ((MalmoModClient.MouseHook) minecraft.mouseHelper).isOverriding = true;
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
     * Immediately switches to Building mode upon receiving the first utterance from the Architect in Thinking mode.
     * Takes a screenshot (on both clients) for all regular chat events.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onClientChatReceived(ClientChatReceivedEvent event) {
        Minecraft minecraft = Minecraft.getMinecraft();
        EntityPlayer player = minecraft.player;
        if (player.getName().equals(MalmoMod.ARCHITECT) && minecraft.playerController.getCurrentGameType() == GameType.SPECTATOR && CwCMod.state == CwCState.THINKING)
            CwCMod.network.sendToServer(new CwCStateMessage(CwCState.BUILDING));

        if (event.getType() == 0) {
            System.out.println("Chat received, type: " + event.getType() + ", message: " + event.getMessage().getUnformattedText() + "; taking screenshot...");
            CwCUtils.takeScreenshot(Minecraft.getMinecraft(), CwCUtils.useTimestamps, CwCScreenshotEventType.CHAT, false); //FIXME
        }
    }

    /**
     * Only allows players, falling blocks, and items to spawn.
     * Initializes the Architect with an empty inventory.
     * If the Builder has an empty inventory, initialize it with default stack sizes of all colored blocks.
     * Allows the player to fly and be immune to damage.
     *
     * @param event
     */
    @SubscribeEvent
    public void onEntitySpawn(EntityJoinWorldEvent event) {
        // only allow player, falling blocks, and items to spawn
        if (!(event.getEntity() instanceof EntityPlayer || event.getEntity() instanceof EntityFallingBlock || event.getEntity() instanceof EntityItem))
            event.setCanceled(true);

        if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer) {
            EntityPlayerMP player = (EntityPlayerMP) event.getEntity();
            System.out.println("onEntitySpawn: " + player.getName());

            // initialize Architect with empty inventory
            if (player.getName().equals(MalmoMod.ARCHITECT) || player.getName().equals(MalmoMod.ORACLE)) {
                for (int i = 0; i < InventoryPlayer.getHotbarSize(); i++)
                    player.inventory.setInventorySlotContents(i, ItemStack.EMPTY);
                return;
            }

            // check for empty inventory
            boolean empty = true;
            for (int i = 0; i < InventoryPlayer.getHotbarSize(); i++) {
                if (!player.inventory.getStackInSlot(i).isEmpty()) {
                    empty = false;
                    break;
                }
            }

            // initialize the inventory
            if (empty) {
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.red, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.orange, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.yellow, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.green, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.blue, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.purple, DEFAULT_STACK_SIZE));
                System.out.println("\t-- inventory INITIALIZED");
            }

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
     * Re-enables flying and damage immunity should the player respawn (hopefully shouldn't be called).
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
     * Switches active hotbar slot to the item just picked up, or first empty slot if the item doesn't exist in hotbar.
     * If, for some reason, the hotbar is full and the item doesn't exist in hotbar already, the currently held item isn't changed.
     *
     * @param event
     */
    @SubscribeEvent
    public void onItemPickup(EntityItemPickupEvent event) {
        if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayerMP) {
            EntityPlayerMP player = (EntityPlayerMP) event.getEntityPlayer();
            System.out.println("Item " + event.getItem().getName() + " picked up by " + player.getName());

            if (event.getItem().getEntityItem().getItem() != Items.AIR) {
                int slot = player.inventory.getSlotFor(event.getItem().getEntityItem());
                int empty = player.inventory.getFirstEmptyStack();
                player.inventory.currentItem = InventoryPlayer.isHotbar(slot) ? slot : empty < 0 ? player.inventory.currentItem : empty;
                player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));
            }
        }
    }

    /**
     * Sets held item to first empty slot upon placing a block. If, for some reason, no hotbar slots are empty, then
     * this does nothing.
     *
     * @param event
     */
    @SubscribeEvent
    public void onBlockPlace(BlockEvent.PlaceEvent event) {
        if (!event.getPlayer().getEntityWorld().isRemote && event.getPlayer() instanceof EntityPlayerMP) {
            EntityPlayerMP player = (EntityPlayerMP) event.getPlayer();
            System.out.println("Block " + event.getPlacedBlock().getBlock().getUnlocalizedName() + " placed by " + player.getName());

            int empty = player.inventory.getFirstEmptyStack();
            player.inventory.currentItem = empty < 0 ? player.inventory.currentItem : empty;
            player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));
        }
    }

    /**
     * Disables falling damage.
     *
     * @param event
     */
    @SubscribeEvent
    public void playerFall(LivingFallEvent event) {
        if (event.getEntity() instanceof EntityPlayer) event.setDistance(0.0F);
    }

    /**
     * Hides health, hunger, and experience bars.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void hideHUD(RenderGameOverlayEvent event) {
        if (event.getType().equals(ElementType.HEALTH) || event.getType().equals(ElementType.FOOD) || event.getType().equals(ElementType.EXPERIENCE))
            event.setCanceled(true);

        Minecraft minecraft = Minecraft.getMinecraft();
        if ((minecraft.player.getName().equals(MalmoMod.ARCHITECT) || minecraft.player.getName().equals(MalmoMod.ORACLE)) && event.getType().equals(ElementType.HOTBAR))
            event.setCanceled(true);
    }
}
