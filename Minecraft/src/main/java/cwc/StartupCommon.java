package cwc;

import net.minecraft.item.ItemBlock;
import net.minecraftforge.fml.common.registry.GameRegistry;

public class StartupCommon {
	public static CwCBlock red, orange, yellow, green, blue, purple;
	public static ItemBlock ired, iorange, iyellow, igreen, iblue, ipurple;
	
	public static void preInitCommon() {
		red = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_red_un"));
		red.setRegistryName("cwc_red_rn");
		GameRegistry.register(red);
		ired = new ItemBlock(red);
		ired.setRegistryName(red.getRegistryName());
		GameRegistry.register(ired);

		orange = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_orange_un"));
		orange.setRegistryName("cwc_orange_rn");
		GameRegistry.register(orange);
		iorange = new ItemBlock(orange);
		iorange.setRegistryName(orange.getRegistryName());
		GameRegistry.register(iorange);

		yellow = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_yellow_un"));
		yellow.setRegistryName("cwc_yellow_rn");
		GameRegistry.register(yellow);
		iyellow = new ItemBlock(yellow);
		iyellow.setRegistryName(yellow.getRegistryName());
		GameRegistry.register(iyellow);

		green = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_green_un"));
		green.setRegistryName("cwc_green_rn");
		GameRegistry.register(green);
		igreen = new ItemBlock(green);
		igreen.setRegistryName(green.getRegistryName());
		GameRegistry.register(igreen);

		blue = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_blue_un"));
		blue.setRegistryName("cwc_blue_rn");
		GameRegistry.register(blue);
		iblue = new ItemBlock(blue);
		iblue.setRegistryName(blue.getRegistryName());
		GameRegistry.register(iblue);

		purple = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_purple_un"));
		purple.setRegistryName("cwc_purple_rn");
		GameRegistry.register(purple);
		ipurple = new ItemBlock(purple);
		ipurple.setRegistryName(purple.getRegistryName());
		GameRegistry.register(ipurple);
	}
	
	public static void initCommon() {}
	public static void postInitCommon() {}
}
