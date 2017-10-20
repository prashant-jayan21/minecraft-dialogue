package cwc;

import com.microsoft.Malmo.MissionHandlers.AbsoluteMovementCommandsImplementation;
import net.minecraft.client.Minecraft;
import net.minecraft.util.MouseHelper;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.SidedProxy;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPostInitializationEvent;
import net.minecraftforge.fml.common.event.FMLPreInitializationEvent;
import net.minecraftforge.fml.common.network.NetworkRegistry;
import net.minecraftforge.fml.common.network.simpleimpl.SimpleNetworkWrapper;
import net.minecraftforge.fml.relauncher.Side;
import org.lwjgl.input.Mouse;

import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;

@Mod(modid = CwCMod.MODID, name = "CwC Blocks Mod", version = CwCMod.VERSION)
public class CwCMod {
	public static final String MODID = "cwcmod";
	public static final String VERSION = "1.00";
	public static SimpleNetworkWrapper network;

	@Mod.Instance(CwCMod.MODID)
	public static CwCMod instance;
	
	@SidedProxy(clientSide="cwc.ClientOnlyProxy", serverSide="cwc.DedicatedServerProxy")
	public static CommonProxy proxy;

	public static boolean enableAIToggle = false;
	public static CwCState state = CwCState.INSPECTING; // initialized to the "Inspecting" state
	public static String[] statusOverlay = {"Architect is inspecting...", "Architect is thinking...", "Builder is building..."};
	public static final DateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd_HH.mm.ss");
	public static File loggingDir;
	public static File screenshotDir;
	static {
		loggingDir = new File("/Users/Anjali/Documents/UIUC/research/CwC/BlocksWorld/Minecraft/cwc-minecraft/");
		if (!loggingDir.exists()) loggingDir.mkdir();
		screenshotDir = new File(loggingDir, "screenshots");
		if (!screenshotDir.exists()) screenshotDir.mkdir();
	}

	@EventHandler
	public void preInit(FMLPreInitializationEvent event) {
		network = NetworkRegistry.INSTANCE.newSimpleChannel("cwc");
		network.registerMessage(AbsoluteMovementCommandsImplementation.TeleportMessageHandler.class, AbsoluteMovementCommandsImplementation.TeleportMessage.class, 0, Side.SERVER);
		network.registerMessage(CwCMessageHandler.class, CwCStateMessage.class, 1, Side.CLIENT);
		network.registerMessage(CwCMessageHandler.class, CwCStateMessage.class, 2, Side.SERVER);
		proxy.preInit();
	}
	
	@EventHandler
	public void init(FMLInitializationEvent event) { proxy.init(); }
	
	@EventHandler
	public void postInit(FMLPostInitializationEvent event) { proxy.postInit(); }
	
	public static String prependModID(String name) { return MODID+":"+name; }
}
