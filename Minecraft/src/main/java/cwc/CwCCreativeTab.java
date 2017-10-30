package cwc;


import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.init.Items;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.util.NonNullList;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

/**
 * A custom inventory tab used in Creative mode that houses the CwC-related items.
 * @author nrynchn2
 */
public class CwCCreativeTab extends CreativeTabs {

    public CwCCreativeTab(int index, String label) {
        super(index, label);
    }

    /**
     * Sets the visible icon on the Creative tab's label to be that of a standard Minecraft book.
     * @return Item stack corresponding to Minecraft book
     */
    @SideOnly(Side.CLIENT)
    @Override
    public ItemStack getTabIconItem() {
        return new ItemStack(Items.BOOK);
    }

    /**
     * Displays only the items whose names contain "cwc" on the tab.
     * @param itemsToShowOnTab List of items to show in the custom Creative tab
     */
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
