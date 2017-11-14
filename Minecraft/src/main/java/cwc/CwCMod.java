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

	public static boolean enableAIToggle = false;		// whether or not the original Malmo AI/Human toggle option is enabled
	public static boolean unlimitedInventory = false;	// whether or not Builder has unlimited inventory of blocks
	public static final int MAX_INVENTORY_SIZE = 5;		// maximum number of blocks that can be held at a time by the Builder (if limited inventory)
	protected static int DEFAULT_STACK_SIZE = 1;		// stack sizes of blocks in inventory upon initialization of Builder (if unlimited inventory)

	public static CwCState state = CwCState.INSPECTING; // mod state: initialized to "Inspecting"
	public static boolean reset = false;

	@EventHandler
	public void preInit(FMLPreInitializationEvent event) {
		// initialize the network channel and register the types of messages that can be sent & received over it
		network = NetworkRegistry.INSTANCE.newSimpleChannel("cwc");

		// player teleportation
		network.registerMessage(AbsoluteMovementCommandsImplementation.TeleportMessageHandler.class, AbsoluteMovementCommandsImplementation.TeleportMessage.class, 0, Side.SERVER);

		// mod state change (Inspecting -> Thinking -> Building)
		network.registerMessage(CwCStateMessageHandler.class, CwCStateMessage.class, 1, Side.CLIENT);
		network.registerMessage(CwCStateMessageHandler.class, CwCStateMessage.class, 2, Side.SERVER);

		// screenshot triggers
		network.registerMessage(CwCScreenshotMessageHandler.class, CwCScreenshotMessage.class, 3, Side.CLIENT);
		network.registerMessage(CwCScreenshotMessageHandler.class, CwCScreenshotMessage.class, 4, Side.SERVER);

		// mission quit
		network.registerMessage(CwCQuitMessageHandler.class, CwCQuitMessage.class, 5, Side.CLIENT);
		network.registerMessage(CwCQuitMessageHandler.class, CwCQuitMessage.class, 6, Side.SERVER);

		// register custom keybinds
		CwCKeybinds.register();

		proxy.preInit();
	}
	
	@EventHandler
	public void init(FMLInitializationEvent event) { proxy.init(); }
	
	@EventHandler
	public void postInit(FMLPostInitializationEvent event) { proxy.postInit(); }
	
	public static String prependModID(String name) { return MODID+":"+name; }

	public static void reset() {
		System.out.println("CwCMod: resetting...");
		state = CwCState.INSPECTING;
		CwCUtils.reset();
		CwCEventHandler.reset();
	}
}
