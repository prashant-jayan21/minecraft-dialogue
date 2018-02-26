package cwc;

import net.minecraft.block.Block;
import net.minecraft.block.material.Material;
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
	protected static List<CwCBlock> cwcBlocks;
	protected static List<Block> cwcMinecraftBlocks;
	protected static List<ItemBlock> cwcItems;
	protected static List<ItemBlock> cwcMinecraftItems;
	protected static List<CwCUnbreakableBlock> cwcUnbreakableBlocks;
	protected static String[] breakableColors = {"red", "orange", "yellow", "green", "blue", "purple"};
	private static String[] unbreakableColors = {"grey", "white"};
	private static CwCCreativeTab cwcCreativeTab;


	public static void preInitCommon() {
		cwcBlocks = new ArrayList<CwCBlock>();
		cwcMinecraftBlocks = new ArrayList<Block>();
		cwcItems = new ArrayList<ItemBlock>();
		cwcMinecraftItems = new ArrayList<ItemBlock>();
		cwcUnbreakableBlocks = new ArrayList<CwCUnbreakableBlock>();

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
			cwcBlocks.add(block);

			Block mcblock = new Block(Material.CAKE).setUnlocalizedName("cwc_minecraft_"+color+"_un");
			mcblock.setRegistryName("cwc_minecraft_"+color+"_rn");
			GameRegistry.register(mcblock);
			cwcMinecraftBlocks.add(mcblock);

			ItemBlock item = new ItemBlock(block);
			item.setRegistryName(block.getRegistryName());
			GameRegistry.register(item);
			cwcItems.add(item);

			ItemBlock mcitem = new ItemBlock(mcblock);
			mcitem.setRegistryName(mcblock.getRegistryName());
			GameRegistry.register(mcitem);
			cwcMinecraftItems.add(mcitem);
		}
	}

	private static void registerUnbreakableBlocks() {
		for (String color : unbreakableColors) {
			CwCUnbreakableBlock block = (CwCUnbreakableBlock)(new CwCUnbreakableBlock().setUnlocalizedName("cwc_unbreakable_"+color+"_un"));
			block.setRegistryName("cwc_unbreakable_"+color+"_rn");
			GameRegistry.register(block);
			cwcUnbreakableBlocks.add(block);
		}
	}

	private static void printBlockIds() {
		for (CwCBlock block : cwcBlocks) System.out.println(Block.getIdFromBlock(block));
		for (Block block : cwcMinecraftBlocks) System.out.println(Block.getIdFromBlock(block));
		for (CwCUnbreakableBlock block : cwcUnbreakableBlocks) System.out.println(Block.getIdFromBlock(block));
	}

	/**
	 * Initializes creative tab(s).
	 * This piece of code effectively overwrites the rest of the creative tabs.
	 * If we want them back, will need to initialize this differently.
	 */
	private static void initializeCreativeTabs() {
		CreativeTabs.CREATIVE_TAB_ARRAY = new CreativeTabs[1];
		cwcCreativeTab = new CwCCreativeTab(0, "cwc_creative_tab") {
			@Override
			@SideOnly(Side.CLIENT)
			public ItemStack getTabIconItem() { return new ItemStack(Item.getItemFromBlock(cwcBlocks.get(0))); }
		};
	}
}
 