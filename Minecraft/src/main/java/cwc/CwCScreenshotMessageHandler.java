package cwc;

import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.world.WorldServer;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.relauncher.Side;

/**
 * Server- & client-side handler for custom screenshot messages.
 * @author nrynchn2
 */
public class CwCScreenshotMessageHandler implements IMessageHandler<CwCScreenshotMessage, IMessage> {

    /**
     * Determines if message is received on the server or the client side and calls their respective message handlers.
     * @param message Screenshot message
     * @param ctx Message context
     * @return null
     */
    public IMessage onMessage(final CwCScreenshotMessage message, MessageContext ctx) {
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
            final Minecraft mc = Minecraft.getMinecraft();
            mc.addScheduledTask(new Runnable() {
                public void run() { processMessageOnClient(message); }
            });
            return null;
        }
    }

    /**
     * Handles messages received on the server. Processes the message by sending it out to all connected clients.
     * @param message Screenshot message
     * @param sender Message sender
     */
    void processMessageOnServer(CwCScreenshotMessage message, EntityPlayerMP sender) {
        for (EntityPlayerMP player : sender.mcServer.getPlayerList().getPlayers())
            CwCMod.network.sendTo(message, player);
    }

    /**
     * Handles messages received on the client. Processes the message by setting the appropriate boolean fields responsible for
     * directing logic for when a screenshot should be taken.
     * @param message Screenshot message
     */
    void processMessageOnClient(CwCScreenshotMessage message) {
        if (message.getType() == CwCScreenshotEventType.PICKUP)
            CwCEventHandler.pickedUpBlock = true;
        else if (message.getType() == CwCScreenshotEventType.PUTDOWN)
            CwCEventHandler.placedBlock = true;
    }
}
