package cwc;

import net.minecraft.block.Block;
import net.minecraft.block.BlockFalling;
import net.minecraft.block.BlockSand;
import net.minecraft.block.material.MapColor;
import net.minecraft.block.material.Material;
import net.minecraft.block.state.IBlockState;
import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.util.BlockRenderLayer;
import net.minecraft.util.EnumBlockRenderType;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

public class CwCBlock extends BlockFalling {
	public CwCBlock() {
		super();
		this.setCreativeTab(CreativeTabs.BUILDING_BLOCKS);
	}
	
	@SideOnly(Side.CLIENT)
	public BlockRenderLayer getBlockLayer() { return BlockRenderLayer.SOLID; }
	
	@Override
	public boolean isOpaqueCube(IBlockState iBlockState) { return true; }
	
	@Override
	public boolean isFullCube(IBlockState iBlockState) { return true; }
	
	@Override
	public EnumBlockRenderType getRenderType(IBlockState iBlockState) { return EnumBlockRenderType.MODEL; }
}
