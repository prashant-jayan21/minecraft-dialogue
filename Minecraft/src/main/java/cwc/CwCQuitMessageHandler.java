package cwc;

import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.world.WorldServer;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.relauncher.Side;

/**
 * Server- & client-side handler for quit messages.
 * @author nrynchn2
 */
public class CwCQuitMessageHandler implements IMessageHandler<CwCQuitMessage, IMessage> {

    /**
     * Determines if message is received on the server or the client side and calls their respective message handlers.
     * @param message Quit message
     * @param ctx Message context
     * @return null
     */
    public IMessage onMessage(final CwCQuitMessage message, MessageContext ctx) {
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
     * @param message Quit message
     * @param sender Message sender
     */
    void processMessageOnServer(CwCQuitMessage message, EntityPlayerMP sender) {
        for (EntityPlayerMP player : sender.mcServer.getPlayerList().getPlayers())
            CwCMod.network.sendTo(message, player);
    }

    /**
     * Handles messages received on the client by setting the appropriate "quit" field in {@link CwCEventHandler}.
     * Kills the player attached to this client and resets the mod state.
     * @param message Quit message
     * @param minecraft Minecraft client instance
     */
    void processMessageOnClient(CwCQuitMessage message, Minecraft minecraft) {
        CwCEventHandler.quit = message.quit();
        if (CwCEventHandler.quit) {
            CwCMod.reset();
            minecraft.player.sendChatMessage("/kill");
        }
    }
}
