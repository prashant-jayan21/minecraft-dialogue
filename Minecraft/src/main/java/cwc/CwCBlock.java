package cwc;

import net.minecraft.block.BlockFalling;
import net.minecraft.util.BlockRenderLayer;
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
}
