package cwc;

import net.minecraft.block.Block;
import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.item.Item;
import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;
import net.minecraftforge.fml.common.registry.GameRegistry;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

import java.util.ArrayList;
import java.util.List;

public class StartupCommon {
	protected static List<CwCBlock> blocks;
	protected static List<ItemBlock> items;
	protected static List<CwCUnbreakableBlock> unbreakables;
	protected static String[] breakableColors = {"red", "orange", "yellow", "green", "blue", "purple"};
	private static String[] unbreakableColors = {"grey", "white"};
	private static CwCCreativeTab cwctab;									 // cwc blocks creative tab

	public static void preInitCommon() {
		blocks = new ArrayList<CwCBlock>();
		items = new ArrayList<ItemBlock>();
		unbreakables = new ArrayList<CwCUnbreakableBlock>();

		registerBreakableBlocks();
		registerUnbreakableBlocks();
		initializeCreativeTabs();
	}
	
	public static void initCommon() {}
	public static void postInitCommon() {}

	/**
	 * Registers colored blocks, unbreakable blocks and their corresponding item registries.
	 */
	private static void registerBreakableBlocks() {
		for (String color : breakableColors) {
			CwCBlock block = (CwCBlock)(new CwCBlock().setUnlocalizedName("cwc_"+color+"_un"));
			block.setRegistryName("cwc_"+color+"_rn");
			GameRegistry.register(block);
			blocks.add(block);

			ItemBlock item = new ItemBlock(block);
			item.setRegistryName(block.getRegistryName());
			GameRegistry.register(item);
			items.add(item);
		}
	}

	private static void registerUnbreakableBlocks() {
		for (String color : unbreakableColors) {
			CwCUnbreakableBlock block = (CwCUnbreakableBlock)(new CwCUnbreakableBlock().setUnlocalizedName("cwc_unbreakable_"+color+"_un"));
			block.setRegistryName("cwc_unbreakable_"+color+"_rn");
			GameRegistry.register(block);
			unbreakables.add(block);
		}
	}

	private static void printBlockIds() {
		for (CwCBlock block : blocks) System.out.println(Block.getIdFromBlock(block));
		for (CwCUnbreakableBlock block : unbreakables) System.out.println(Block.getIdFromBlock(block));
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
			public ItemStack getTabIconItem() { return new ItemStack(Item.getItemFromBlock(blocks.get(0))); }
		};
	}
}
 