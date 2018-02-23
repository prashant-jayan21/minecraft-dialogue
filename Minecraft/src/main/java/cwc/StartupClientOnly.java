package cwc;

import com.microsoft.Malmo.Client.MalmoModClient;
import com.microsoft.Malmo.MalmoMod;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.block.model.ModelResourceLocation;
import net.minecraft.item.ItemBlock;
import net.minecraftforge.client.model.ModelLoader;

public class StartupClientOnly {
	public static void preInitClientOnly() {
		final int DEFAULT_ITEM_SUBTYPE = 0;

		// Registers item resource locations of our custom blocks.
		for (int i = 0; i < StartupCommon.items.size(); i++)
			ModelLoader.setCustomModelResourceLocation(StartupCommon.items.get(i), DEFAULT_ITEM_SUBTYPE, new ModelResourceLocation("cwcmod:cwc_"+StartupCommon.breakableColors[i],"inventory"));
	}

	public static void initClientOnly() {}
	public static void postInitClientOnly() {}
}
