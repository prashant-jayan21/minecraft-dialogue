package cwc;

import net.minecraft.client.renderer.block.model.ModelResourceLocation;
import net.minecraftforge.client.model.ModelLoader;

public class StartupClientOnly {
	public static void preInitClientOnly() {
		final int DEFAULT_ITEM_SUBTYPE = 0;

		// cookie loves jelly!
		ModelLoader.setCustomModelResourceLocation(StartupCommon.ired, DEFAULT_ITEM_SUBTYPE, new ModelResourceLocation("cwcmod:cwc_red","inventory"));
		ModelLoader.setCustomModelResourceLocation(StartupCommon.iorange, DEFAULT_ITEM_SUBTYPE, new ModelResourceLocation("cwcmod:cwc_orange","inventory"));
		ModelLoader.setCustomModelResourceLocation(StartupCommon.iyellow, DEFAULT_ITEM_SUBTYPE, new ModelResourceLocation("cwcmod:cwc_yellow","inventory"));
		ModelLoader.setCustomModelResourceLocation(StartupCommon.igreen, DEFAULT_ITEM_SUBTYPE, new ModelResourceLocation("cwcmod:cwc_green","inventory"));
		ModelLoader.setCustomModelResourceLocation(StartupCommon.iblue, DEFAULT_ITEM_SUBTYPE, new ModelResourceLocation("cwcmod:cwc_blue","inventory"));
		ModelLoader.setCustomModelResourceLocation(StartupCommon.ipurple, DEFAULT_ITEM_SUBTYPE, new ModelResourceLocation("cwcmod:cwc_purple","inventory"));
	}

	public static void initClientOnly() {}
	public static void postInitClientOnly() {}
}
