package cwc;

import net.minecraftforge.common.MinecraftForge;

public abstract class CommonProxy {
	public void preInit()  { StartupCommon.preInitCommon(); }

	public void init() {
		StartupCommon.initCommon();
		MinecraftForge.EVENT_BUS.register(new CwCEventHandler()); // register our event handler
	}

	public void postInit() { StartupCommon.postInitCommon(); }
}
