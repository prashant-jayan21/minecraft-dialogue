package cwc;

import com.microsoft.Malmo.MissionHandlers.AbsoluteMovementCommandsImplementation;
import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.world.WorldServer;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.relauncher.Side;
import org.lwjgl.opengl.Display;

import static cwc.CwCUtils.playerNameMatches;
import static cwc.CwCUtils.playerNameMatchesAny;

public class CwCInitializationMessageHandler implements IMessageHandler<CwCInitializationMessage, IMessage> {

    /**
     * Determines if message is received on the server or the client side and calls their respective message handlers.
     *
     * @param message Initialization message
     * @param ctx     Message context
     * @return null
     */
    public IMessage onMessage(final CwCInitializationMessage message, MessageContext ctx) {
        // process message on server
        if (ctx.side == Side.SERVER) {
            final EntityPlayerMP sender = ctx.getServerHandler().playerEntity;
            if (ctx.getServerHandler().playerEntity == null) return null;

            final WorldServer pws = sender.getServerWorld();
            pws.addScheduledTask(new Runnable() {
                public void run() {
                    processMessageOnServer(message, sender);
                }
            });
            return null;
        }

        // process message on client
        else {
            final Minecraft mc = Minecraft.getMinecraft();
            mc.addScheduledTask(new Runnable() {
                public void run() {
                    processMessageOnClient(mc);
                }
            });
            return null;
        }
    }

    /**
     * Handles messages received on the server. Processes the message by sending it out to all connected clients.
     *
     * @param message Initialization message
     * @param sender  Message sender
     */
    void processMessageOnServer(CwCInitializationMessage message, EntityPlayerMP sender) {
        System.out.println("Server received: initialization message by "+sender.getName());
        for (EntityPlayerMP player : sender.mcServer.getPlayerList().getPlayers())
            CwCMod.network.sendTo(message, player);
    }

    /**
     * Handles messages received on the client.
     *
     * @param mc Minecraft client instance
     */
    void processMessageOnClient(Minecraft mc) {
        System.out.println("Initialization message received by "+mc.player.getName());
        CwCMod.reset();
        Display.setTitle(mc.player.getName());
    }
}
