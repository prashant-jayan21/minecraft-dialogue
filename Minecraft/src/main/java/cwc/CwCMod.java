package cwc;

import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.SidedProxy;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPostInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPreInitializationEvent;

@Mod(modid = CwCMod.MODID, name = "CwC Blocks Mod", version = CwCMod.VERSION)
public class CwCMod {
	public static final String MODID = "cwcmod";
	public static final String VERSION = "1.00";
	
	@Mod.Instance(CwCMod.MODID)
	public static CwCMod instance;
	
	@SidedProxy(clientSide="cwc.ClientOnlyProxy", serverSide="cwc.DedicatedServerProxy")
	public static CommonProxy proxy;
	
	@EventHandler
	public void preInit(FMLPreInitializationEvent event) { proxy.preInit(); }
	
	@EventHandler
	public void init(FMLInitializationEvent event) { proxy.init(); }
	
	@EventHandler
	public void postInit(FMLPostInitializationEvent event) { proxy.postInit(); }
	
	public static String prependModID(String name) { return MODID+":"+name; }
}
