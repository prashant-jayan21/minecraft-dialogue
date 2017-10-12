package cwc;

import com.microsoft.Malmo.MissionHandlers.AbsoluteMovementCommandsImplementation;
import net.minecraft.client.Minecraft;
import net.minecraft.client.entity.EntityPlayerSP;
import net.minecraft.client.settings.GameSettings;
import net.minecraft.entity.item.EntityFallingBlock;
import net.minecraft.entity.item.EntityItem;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.entity.player.InventoryPlayer;
import net.minecraft.init.Items;
import net.minecraft.item.ItemStack;
import net.minecraft.network.play.server.SPacketHeldItemChange;
import net.minecraft.world.GameType;
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

    private static int DEFAULT_STACK_SIZE = 10;
    private static boolean spectating = false;

    /**
     * Ignore keybindings: drop, use item, swap hands, open inventory, player list, commands, screenshots, toggle perspective,
     * smooth camera, and spectator outlines.
     * Upon pressing E, the Architect can assume mob-view of the Builder. While in this mode, the Architect can switch between
     * first- and third-person views by pressing F.
     *
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onKeyInput(KeyInputEvent event) {
        Minecraft minecraft = Minecraft.getMinecraft();
        GameSettings gs = minecraft.gameSettings;
        EntityPlayerSP player = minecraft.player;

        // press E as Architect to instantly assume the point of view of the builder
        if (player.getName().equals("Architect") && minecraft.playerController.getCurrentGameType() == GameType.SPECTATOR && gs.keyBindInventory.isPressed()) {
            if (!spectating) {
                EntityPlayer builder = null;
                for (EntityPlayer ep : Minecraft.getMinecraft().world.playerEntities)
                    if (ep.getName().equals("Builder")) builder = ep;

                if (builder != null) {
                    CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(builder.posX, builder.posY, builder.posZ, 0, 0, true, true, true, true, true));
                    minecraft.playerController.attackEntity(Minecraft.getMinecraft().player, builder);
                    spectating = true;
                } else System.out.println("ERROR: Builder not found (null)");
            } else {
                // TODO: can we send a packet to the server to enable sneaking and get out of mob-view?
//                gs.thirdPersonView = 0;
//                spectating = false;
            }
        }

        // FIXME: because "E" to stop spectating isn't implemented yet
        else if (player.getName().equals("Architect") && minecraft.playerController.getCurrentGameType() == GameType.SPECTATOR && gs.keyBindSneak.isPressed()) {
            gs.thirdPersonView = 0;
            spectating = false;
        }

        // press F to switch between first- and third-person views (TODO: should this only be available to architect?)
        else if (gs.keyBindSwapHands.isPressed() && (player.getName().equals("Builder") || (player.getName().equals("Architect") && spectating)))
            gs.thirdPersonView = gs.thirdPersonView == 1 ? 0 : 1;

        else if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                gs.keyBindInventory.isPressed() || gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() ||
                gs.keyBindScreenshot.isPressed() || gs.keyBindTogglePerspective.isPressed() ||
                gs.keyBindSmoothCamera.isPressed() || gs.keyBindSpectatorOutlines.isPressed());
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
            if (player.getName().equals("Architect")) {
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
     * Prevents noclipping through floor.
     *
     * @param event
     */
    @SubscribeEvent
    public void playerMove(LivingEvent.LivingUpdateEvent event) {
        EntityPlayer player = (EntityPlayer) event.getEntity();
        if (player.posY < 0) {
            event.setCanceled(true);
            player.setPositionAndUpdate(player.posX, 0, player.posZ);
        }
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

        if (Minecraft.getMinecraft().player.getName().equals("Architect") && event.getType().equals(ElementType.HOTBAR))
            event.setCanceled(true);
    }
}
