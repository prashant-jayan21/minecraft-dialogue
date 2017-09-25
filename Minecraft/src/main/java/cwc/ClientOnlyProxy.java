package cwc;

public class ClientOnlyProxy extends CommonProxy {
	public void preInit() { 
		super.preInit();
		StartupClientOnly.preInitClientOnly();
	}
	
	public void init() {
		super.init();
		StartupClientOnly.initClientOnly();
	}
	
	public void postInit() {
		super.postInit();
		StartupClientOnly.postInitClientOnly();
	}
}
