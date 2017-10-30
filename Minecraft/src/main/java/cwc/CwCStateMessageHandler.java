package cwc;

import com.microsoft.Malmo.Client.MalmoModClient;
import com.microsoft.Malmo.MalmoMod;
import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.world.WorldServer;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.relauncher.Side;

/**
 * Server- & client-side handler for custom mod state change messages.
 * @author nrynchn2
 */
public class CwCStateMessageHandler implements IMessageHandler<CwCStateMessage, IMessage> {

    /**
     * Determines if message is received on the server or the client side and calls their respective message handlers.
     * @param message State change message
     * @param ctx Message context
     * @return null
     */
    public IMessage onMessage(final CwCStateMessage message, MessageContext ctx) {
        // process message on server
        if (ctx.side == Side.SERVER) {
            final EntityPlayerMP sender = ctx.getServerHandler().playerEntity;
            if (ctx.getServerHandler().playerEntity == null) return null;

            final WorldServer pws = sender.getServerWorld();
            pws.addScheduledTask(new Runnable() {
                public void run() { processMessageOnServer(message, sender); }
            });
            return null;
        }

        // process message on client
        else {
            final Minecraft minecraft = Minecraft.getMinecraft();
            minecraft.addScheduledTask(new Runnable() {
                public void run() { processMessageOnClient(message, minecraft); }
            });
            return null;
        }
    }

    /**
     * Handles messages received on the server. Processes the message by sending it out to all connected clients.
     * @param message State change message
     * @param sender Message sender
     */
    void processMessageOnServer(CwCStateMessage message, EntityPlayerMP sender) {
        for (EntityPlayerMP player : sender.mcServer.getPlayerList().getPlayers())
            CwCMod.network.sendTo(message, player);
    }

    /**
     * Handles messages received on the client. Processes the message by setting the appropriate fields, as well as enabling reset
     * and overriding/releasing the mouse.
     * @param message State change message
     * @param mc Minecraft client
     */
    void processMessageOnClient(CwCStateMessage message, Minecraft mc) {
        CwCMod.state = CwCState.valueOf(message.getState());
        EntityPlayer player = mc.player;

        // when switching to Inspecting, set the reset field to prompt Architect to exit mob-view and override the Builder's mouse
        if (CwCMod.state == CwCState.INSPECTING) {
            CwCEventHandler.reset = true;
            if (player.getName().equals(MalmoMod.BUILDER) && mc.mouseHelper instanceof MalmoModClient.MouseHook)
                ((MalmoModClient.MouseHook) mc.mouseHelper).isOverriding = true;
        }

        // when switching to Building, return mouse control to the Builder
        else if (CwCMod.state == CwCState.BUILDING && player.getName().equals(MalmoMod.BUILDER) && mc.mouseHelper instanceof MalmoModClient.MouseHook)
            ((MalmoModClient.MouseHook) mc.mouseHelper).isOverriding = false;
    }
}
