package cwc;

import net.minecraft.client.settings.KeyBinding;
import net.minecraftforge.fml.client.registry.ClientRegistry;
import org.lwjgl.input.Keyboard;

/**
 * Custom keybinds specific to the CwC Mod.
 */
public class CwCKeybinds {
    public static KeyBinding quitCtrl;  // ctrl + Q: quit
    public static KeyBinding quitKeyQ;
    // public static KeyBinding gold;  // G: switch to gold configuration (available only in Inspecting mode)

    /**
     * Registers the custom keybinds.
     */
    public static void register() {
        quitCtrl = new KeyBinding("key.quit-ctrl", Keyboard.KEY_LCONTROL, "key.categories.cwc");
        quitKeyQ = new KeyBinding("key.quit-q", Keyboard.KEY_Q, "key.categories.cwc");
        ClientRegistry.registerKeyBinding(quitCtrl);
        ClientRegistry.registerKeyBinding(quitKeyQ);
    }
}
