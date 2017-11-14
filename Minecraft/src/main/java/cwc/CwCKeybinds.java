package cwc;

import net.minecraft.client.settings.KeyBinding;
import net.minecraftforge.fml.client.registry.ClientRegistry;
import org.lwjgl.input.Keyboard;

/**
 * Custom keybinds specific to the CwC Mod.
 */
public class CwCKeybinds {
    public static KeyBinding quit;  // ESC: quit
    public static KeyBinding gold;  // G: switch to gold configuration (available only in Inspecting mode)

    /**
     * Registers the custom keybinds.
     */
    public static void register() {
        quit = new KeyBinding("key.quit", Keyboard.KEY_ESCAPE, "key.categories.cwc");
        gold = new KeyBinding("key.gold", Keyboard.KEY_G, "key.categories.cwc");
        ClientRegistry.registerKeyBinding(quit);
        ClientRegistry.registerKeyBinding(gold);
    }
}
