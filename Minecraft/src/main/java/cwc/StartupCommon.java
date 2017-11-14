package cwc;

import net.minecraft.block.Block;
import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.item.Item;
import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;
import net.minecraftforge.fml.common.registry.GameRegistry;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

public class StartupCommon {
	protected static CwCBlock red, orange, yellow, green, blue, purple;		 // colored blocks
	protected static ItemBlock ired, iorange, iyellow, igreen, iblue, ipurple;  // colored item blocks
	private static CwCUnbreakableBlock unb_grey, unb_white;	 				 // unbreakable blocks
	private static CwCTransparentBlock unb_transparent;
	private static CwCCreativeTab cwctab;									 // cwc blocks creative tab

	public static void preInitCommon() {
		registerBlocks();
		initializeCreativeTabs();
	}
	
	public static void initCommon() {}
	public static void postInitCommon() {}

	/**
	 * Registers colored blocks, unbreakable blocks and their corresponding item registries.
	 */
	private static void registerBlocks() {
		// red
		red = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_red_un"));
		red.setRegistryName("cwc_red_rn");
		GameRegistry.register(red);
		ired = new ItemBlock(red);
		ired.setRegistryName(red.getRegistryName());
		GameRegistry.register(ired);

		// orange
		orange = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_orange_un"));
		orange.setRegistryName("cwc_orange_rn");
		GameRegistry.register(orange);
		iorange = new ItemBlock(orange);
		iorange.setRegistryName(orange.getRegistryName());
		GameRegistry.register(iorange);

		// yellow
		yellow = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_yellow_un"));
		yellow.setRegistryName("cwc_yellow_rn");
		GameRegistry.register(yellow);
		iyellow = new ItemBlock(yellow);
		iyellow.setRegistryName(yellow.getRegistryName());
		GameRegistry.register(iyellow);

		// green
		green = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_green_un"));
		green.setRegistryName("cwc_green_rn");
		GameRegistry.register(green);
		igreen = new ItemBlock(green);
		igreen.setRegistryName(green.getRegistryName());
		GameRegistry.register(igreen);

		// blue
		blue = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_blue_un"));
		blue.setRegistryName("cwc_blue_rn");
		GameRegistry.register(blue);
		iblue = new ItemBlock(blue);
		iblue.setRegistryName(blue.getRegistryName());
		GameRegistry.register(iblue);

		// purple
		purple = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_purple_un"));
		purple.setRegistryName("cwc_purple_rn");
		GameRegistry.register(purple);
		ipurple = new ItemBlock(purple);
		ipurple.setRegistryName(purple.getRegistryName());
		GameRegistry.register(ipurple);

		// grey, unbreakable
		unb_grey = (CwCUnbreakableBlock)(new CwCUnbreakableBlock().setUnlocalizedName("cwc_unbreakable_grey_un"));
		unb_grey.setRegistryName("cwc_unbreakable_grey_rn");
		GameRegistry.register(unb_grey);

		// white, unbreakable
		unb_white = (CwCUnbreakableBlock)(new CwCUnbreakableBlock().setUnlocalizedName("cwc_unbreakable_white_un"));
		unb_white.setRegistryName("cwc_unbreakable_white_rn");
		GameRegistry.register(unb_white);

		// transparent, unbreakable (skybox)
		unb_transparent = (CwCTransparentBlock)(new CwCTransparentBlock().setUnlocalizedName("cwc_unbreakable_transparent_un"));
		unb_transparent.setRegistryName("cwc_unbreakable_transparent_rn");
		GameRegistry.register(unb_transparent);

		// show block IDs of custom blocks -- add statements as needed
		System.out.println("Red block ID: "+Block.getIdFromBlock(red));
		System.out.println("Orange block ID: "+Block.getIdFromBlock(orange));
		System.out.println("Yellow block ID: "+Block.getIdFromBlock(yellow));
		System.out.println("Green block ID: "+Block.getIdFromBlock(green));
		System.out.println("Blue block ID: "+Block.getIdFromBlock(blue));
		System.out.println("Purple block ID: "+Block.getIdFromBlock(purple));
		System.out.println("Unbreakable grey block ID: "+Block.getIdFromBlock(unb_grey));
		System.out.println("Unbreakable white block ID: "+Block.getIdFromBlock(unb_white));
		System.out.println("Transparent block ID: "+Block.getIdFromBlock(unb_transparent));
	}

	/**
	 * Initializes creative tab(s).
	 * This piece of code effectively overwrites the rest of the creative tabs.
	 * If we want them back, will need to initialize this differently.
	 */
	private static void initializeCreativeTabs() {
		CreativeTabs.CREATIVE_TAB_ARRAY = new CreativeTabs[1];
		cwctab = new CwCCreativeTab(0, "cwc_creative_tab") {
			@Override
			@SideOnly(Side.CLIENT)
			public ItemStack getTabIconItem() { return new ItemStack(Item.getItemFromBlock(red)); }
		};
	}
}
 