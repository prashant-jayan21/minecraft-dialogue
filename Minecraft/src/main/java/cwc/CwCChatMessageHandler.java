package cwc;

import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.world.WorldServer;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.relauncher.Side;

/**
 * Server- & client-side handler for chat status messages.
 * @author nrynchn2
 */
public class CwCChatMessageHandler implements IMessageHandler<CwCChatMessage, IMessage> {

    /**
     * Determines if message is received on the server or the client side and calls their respective message handlers.
     * @param message Chat message
     * @param ctx Message context
     * @return null
     */
    public IMessage onMessage(final CwCChatMessage message, MessageContext ctx) {
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
     * Handles messages received on the server. Processes the message by sending it out to all other connected clients.
     * @param message Chat message
     * @param sender Message sender
     */
    void processMessageOnServer(CwCChatMessage message, EntityPlayerMP sender) {
        for (EntityPlayerMP player : sender.mcServer.getPlayerList().getPlayers())
            if (!player.getName().equals(sender.getName())) CwCMod.network.sendTo(message, player);
    }

    /**
     * Handles messages received on the client by setting the appropriate "chatting" field in {@link CwCEventHandler}.
     * @param message Chat message
     * @param minecraft Minecraft client instance
     */
    void processMessageOnClient(CwCChatMessage message, Minecraft minecraft) {
        CwCEventHandler.partnerIsChatting = message.chatting();
    }
}
