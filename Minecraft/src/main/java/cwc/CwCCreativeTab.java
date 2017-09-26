package cwc;


import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.init.Items;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.util.NonNullList;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

public class CwCCreativeTab extends CreativeTabs {

    public CwCCreativeTab(int index, String label) {
        super(index, label);
    }

    @SideOnly(Side.CLIENT)
    @Override
    public ItemStack getTabIconItem() {
        return new ItemStack(Items.BOOK);
    }

    @SideOnly(Side.CLIENT)
    @Override
    public void displayAllRelevantItems(NonNullList<ItemStack> itemsToShowOnTab) {
        for (Item item : Item.REGISTRY) {
            if (item != null) {
                if (item.getUnlocalizedName().contains("cwc")) {
                    item.getSubItems(item, this, itemsToShowOnTab);  // add all sub items to the list
                }
            }
        }
    }

}
