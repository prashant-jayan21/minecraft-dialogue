package cwc;

import net.minecraft.block.BlockFalling;
import net.minecraft.block.state.IBlockState;
import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.util.BlockRenderLayer;
import net.minecraft.util.EnumBlockRenderType;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.World;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

public class CwCBlock extends BlockFalling {
	public CwCBlock() {
		super();
		this.setBlockUnbreakable();
		this.setResistance(6000000.0F);
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
