package cwc;

import net.minecraft.client.settings.KeyBinding;
import net.minecraftforge.fml.client.registry.ClientRegistry;
import org.lwjgl.input.Keyboard;

/**
 * Custom keybinds specific to the CwC Mod.
 */
public class CwCKeybinds {
    public static KeyBinding quitCtrl;  // ctrl + C: quit
    public static KeyBinding quitKeyC;

    /**
     * Registers the custom keybinds.
     */
    public static void register() {
        quitCtrl = new KeyBinding("key.quit-ctrl", Keyboard.KEY_LCONTROL, "key.categories.cwc");
        quitKeyC = new KeyBinding("key.quit-q", Keyboard.KEY_C, "key.categories.cwc");
        ClientRegistry.registerKeyBinding(quitCtrl);
        ClientRegistry.registerKeyBinding(quitKeyC);
    }
}
