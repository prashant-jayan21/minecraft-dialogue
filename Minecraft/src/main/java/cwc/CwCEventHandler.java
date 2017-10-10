package cwc;

import net.minecraft.client.Minecraft;
import net.minecraft.client.settings.GameSettings;
import net.minecraft.entity.item.EntityFallingBlock;
import net.minecraft.entity.item.EntityItem;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.entity.player.InventoryPlayer;
import net.minecraft.init.Items;
import net.minecraft.item.ItemStack;
import net.minecraft.network.play.server.SPacketHeldItemChange;
import net.minecraftforge.event.entity.EntityJoinWorldEvent;
import net.minecraftforge.event.entity.living.LivingFallEvent;
import net.minecraftforge.event.entity.player.EntityItemPickupEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.world.BlockEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.InputEvent.*;
import net.minecraftforge.fml.common.network.NetworkRegistry;
import net.minecraftforge.fml.common.network.simpleimpl.SimpleNetworkWrapper;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

public class CwCEventHandler {

    public static SimpleNetworkWrapper network = NetworkRegistry.INSTANCE.newSimpleChannel("cwc");
    private static int DEFAULT_STACK_SIZE = 10;

    /**
     * Ignore some keybindings.
     * @param event
     */
    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onKeyInput(KeyInputEvent event) {
        GameSettings gs = Minecraft.getMinecraft().gameSettings;
        if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() || gs.keyBindInventory.isPressed() ||
                gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() || gs.keyBindScreenshot.isPressed() ||
                gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() || gs.keyBindSpectatorOutlines.isPressed());
    }

    /**
     * Only allows players, falling blocks, and items to spawn.
     * If the player has an empty inventory, initialize it with default stack sizes of all colored blocks.
     * Allows the player to fly and be immune to damage.
     * @param event
     */
    @SubscribeEvent
    public void onEntitySpawn(EntityJoinWorldEvent event) {
        if (!(event.getEntity() instanceof EntityPlayer || event.getEntity() instanceof EntityFallingBlock || event.getEntity() instanceof EntityItem))
            event.setCanceled(true);

        if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer) {
            EntityPlayer player = (EntityPlayer) event.getEntity();
            System.out.println("onEntitySpawn: "+player.getName());

            boolean empty = true;
            for (int i = 0; i < InventoryPlayer.getHotbarSize(); i++) {
                if (!player.inventory.getStackInSlot(i).isEmpty()) {
                    empty = false;
                    break;
                }
            }

            if (empty) {
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.red, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.orange, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.yellow, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.green, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.blue, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.purple, DEFAULT_STACK_SIZE));
                System.out.println("\t-- inventory INITIALIZED");
            }

            player.capabilities.allowFlying = true;
            player.capabilities.disableDamage = true;
            player.sendPlayerAbilities();
            System.out.println("\t-- flying capabilities ON, damage OFF");
        }
    }

    /**
     * Re-enables flying and damage immunity should the player respawn (hopefully shouldn't be called).
     * @param event
     */
    @SubscribeEvent
    public void onPlayerClone(PlayerEvent.Clone event) {
        if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer) {
            EntityPlayer player = event.getEntityPlayer();
            System.out.println("onPlayerClone: "+player.getName());
            player.capabilities.allowFlying = true;
            player.capabilities.disableDamage = true;
            player.sendPlayerAbilities();
            System.out.println("\t-- flying capabilities ON, damage OFF");
        }
    }

    /**
     * Switches active hotbar slot to the item just picked up, or first empty slot if the item doesn't exist in hotbar.
     * If, for some reason, the hotbar is full and the item doesn't exist in hotbar already, the currently held item isn't changed.
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
     * @param event
     */
    @SubscribeEvent
    public void onBlockPlace(BlockEvent.PlaceEvent event) {
        if (!event.getPlayer().getEntityWorld().isRemote && event.getPlayer() instanceof EntityPlayerMP) {
            EntityPlayerMP player = (EntityPlayerMP) event.getPlayer();
            System.out.println("Block "+event.getPlacedBlock().getBlock().getUnlocalizedName()+" placed by "+player.getName());

            int empty = player.inventory.getFirstEmptyStack();
            player.inventory.currentItem = empty < 0 ? player.inventory.currentItem : empty;
            player.connection.sendPacket(new SPacketHeldItemChange(player.inventory.currentItem));
        }
    }

    /**
     * Disables falling damage.
     * @param event
     */
    @SubscribeEvent
    public void playerFall(LivingFallEvent event) {
        if (event.getEntity() instanceof EntityPlayer) event.setDistance(0.0F);
    }

}
