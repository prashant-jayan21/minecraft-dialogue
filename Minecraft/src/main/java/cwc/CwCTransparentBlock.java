package cwc;

import net.minecraft.block.Block;
import net.minecraft.block.material.Material;
import net.minecraft.block.state.IBlockState;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.util.BlockRenderLayer;
import net.minecraft.util.EnumFacing;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.IBlockAccess;
import net.minecraft.world.World;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

public class CwCTransparentBlock extends Block {
    public CwCTransparentBlock() {
        super(Material.GLASS);
        this.setBlockUnbreakable();
        this.setResistance(6000000.0F);
    }

    @SideOnly(Side.CLIENT)
    public BlockRenderLayer getBlockLayer() { return BlockRenderLayer.TRANSLUCENT; }

    @Override
    public boolean removedByPlayer(IBlockState state, World world, BlockPos pos, EntityPlayer player, boolean willHarvest) { return false; }

}
