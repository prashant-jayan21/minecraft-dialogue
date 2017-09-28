package cwc;

import net.minecraft.client.Minecraft;
import net.minecraft.client.settings.GameSettings;
import net.minecraft.entity.item.EntityFallingBlock;
import net.minecraft.entity.item.EntityItem;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.item.ItemStack;
import net.minecraftforge.event.entity.EntityJoinWorldEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.InputEvent.*;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

public class CwCEventHandler {

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
            if (player.inventory.getStackInSlot(0).isEmpty()) {
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.red, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.orange, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.yellow, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.green, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.blue, DEFAULT_STACK_SIZE));
                player.inventory.addItemStackToInventory(new ItemStack(StartupCommon.purple, DEFAULT_STACK_SIZE));
            }

            player.capabilities.allowFlying = true;
            player.capabilities.disableDamage = true;
            player.sendPlayerAbilities();
            System.out.println("Player created -- flying capabilities ON");
        }
    }

    /**
     * Re-enables flying and damage immunity should the player respawn (hopefully shouldn't be called).
     * @param event
     */
    @SubscribeEvent
    public void onPlayerClone(PlayerEvent.Clone event) {
        if (!event.getEntity().getEntityWorld().isRemote && event.getEntity() instanceof EntityPlayer) {
            EntityPlayer player = (EntityPlayer) event.getEntity();
            player.capabilities.allowFlying = true;
            player.capabilities.disableDamage = true;
            player.sendPlayerAbilities();
            System.out.println("Player respawned -- flying capabilities ON");
        }
    }

}
