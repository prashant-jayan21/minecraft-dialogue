package cwc;

import net.minecraft.client.Minecraft;
import net.minecraft.client.settings.GameSettings;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.InputEvent.*;

public class CwCEventHandler {

    @SubscribeEvent
    public void onKeyInput(KeyInputEvent event) {
        GameSettings gs = Minecraft.getMinecraft().gameSettings;
        if (gs.keyBindDrop.isPressed() || gs.keyBindSwapHands.isPressed() || gs.keyBindUseItem.isPressed() ||
                gs.keyBindPlayerList.isPressed() || gs.keyBindCommand.isPressed() || gs.keyBindScreenshot.isPressed() ||
                gs.keyBindTogglePerspective.isPressed() || gs.keyBindSmoothCamera.isPressed() || gs.keyBindSpectatorOutlines.isPressed());
    }
}
