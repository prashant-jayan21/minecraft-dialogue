package cwc;

public abstract class CommonProxy {
	public void preInit()  { StartupCommon.preInitCommon(); }
	public void init()     { StartupCommon.initCommon(); }
	public void postInit() { StartupCommon.postInitCommon(); }
}
