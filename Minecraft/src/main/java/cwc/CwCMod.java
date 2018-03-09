package cwc;

import com.microsoft.Malmo.MissionHandlers.AbsoluteMovementCommandsImplementation;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.SidedProxy;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPostInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPreInitializationEvent;
import net.minecraftforge.fml.common.network.NetworkRegistry;
import net.minecraftforge.fml.common.network.simpleimpl.SimpleNetworkWrapper;
import net.minecraftforge.fml.relauncher.Side;

import java.util.ArrayList;

/**
 * The CwC mod.
 * @author nrynchn2
 */
@Mod(modid = CwCMod.MODID, name = "CwC Blocks Mod", version = CwCMod.VERSION)
public class CwCMod {
	public static final String MODID = "cwcmod"; // mod ID: prepends registry names of mod-specific blocks and items
	public static final String VERSION = "1.00"; // mod version
	public static SimpleNetworkWrapper network;  // mod network: mod-specific packets sent and received over this channel

	@Mod.Instance(CwCMod.MODID)
	public static CwCMod instance;				 // mod instance
	
	@SidedProxy(clientSide="cwc.ClientOnlyProxy", serverSide="cwc.DedicatedServerProxy")
	public static CommonProxy proxy;			 // mod proxy

	public static final String ARCHITECT = "Architect";
	public static final String BUILDER = "Builder";
	public static final String ORACLE = "Oracle";
	public static String[] FIXED_VIEWERS;

	public static boolean enableAIToggle = false;		// whether or not the original Malmo AI/Human toggle option is enabled
	public static final int DEFAULT_STACK_SIZE = 20;	// stack size of blocks in Builder's inventory
	protected static int NUM_FIXED_VIEWERS = 4;

	static {
		FIXED_VIEWERS = new String[NUM_FIXED_VIEWERS];
		for (int i = 0; i < NUM_FIXED_VIEWERS; i++)
			FIXED_VIEWERS[i] = "FixedViewer"+(i+1);
	}

	public static ArrayList<String> screenshots = new ArrayList<String>();  // list of absolute paths of screenshots taken by the client

	@EventHandler
	public void preInit(FMLPreInitializationEvent event) {
		// initialize the network channel and register the types of messages that can be sent & received over it
		network = NetworkRegistry.INSTANCE.newSimpleChannel("cwc");

		// player teleportation
		network.registerMessage(AbsoluteMovementCommandsImplementation.TeleportMessageHandler.class, AbsoluteMovementCommandsImplementation.TeleportMessage.class, 0, Side.SERVER);

		// screenshot triggers
		network.registerMessage(CwCScreenshotMessageHandler.class, CwCScreenshotMessage.class, 1, Side.CLIENT);
		network.registerMessage(CwCScreenshotMessageHandler.class, CwCScreenshotMessage.class, 2, Side.SERVER);

		// mission quit
		network.registerMessage(CwCQuitMessageHandler.class, CwCQuitMessage.class, 3, Side.CLIENT);
		network.registerMessage(CwCQuitMessageHandler.class, CwCQuitMessage.class, 4, Side.SERVER);

		// partner chatting
		network.registerMessage(CwCChatMessageHandler.class, CwCChatMessage.class, 5, Side.CLIENT);
		network.registerMessage(CwCChatMessageHandler.class, CwCChatMessage.class, 6, Side.SERVER);

		// builder position
		network.registerMessage(CwCPositionMessageHandler.class, CwCPositionMessage.class, 7, Side.CLIENT);
		network.registerMessage(CwCPositionMessageHandler.class, CwCPositionMessage.class, 8, Side.SERVER);

		network.registerMessage(CwCInitializationMessageHandler.class, CwCInitializationMessage.class, 9, Side.CLIENT);
		network.registerMessage(CwCInitializationMessageHandler.class, CwCInitializationMessage.class, 10, Side.SERVER);

		// register custom keybinds
		CwCKeybinds.register();

		proxy.preInit();
	}
	
	@EventHandler
	public void init(FMLInitializationEvent event) { proxy.init(); }
	
	@EventHandler
	public void postInit(FMLPostInitializationEvent event) { proxy.postInit(); }
	
	public static String prependModID(String name) { return MODID+":"+name; }

	/**
	 * Resets all required fields associated with the mod.
	 */
	public static void reset() {
		System.out.println("CwCMod: resetting...");
		CwCUtils.reset();
		CwCEventHandler.reset();
	}
}
