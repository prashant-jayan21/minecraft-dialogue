package cwc;

import com.microsoft.Malmo.MissionHandlers.AbsoluteMovementCommandsImplementation;
import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.world.WorldServer;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.relauncher.Side;

import static cwc.CwCEventHandler.playerNameMatches;

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
                    processMessageOnClient(message, mc);
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
     * @param message   Initialization message
     * @param mc        Minecraft client instance
     */
    void processMessageOnClient(CwCInitializationMessage message, Minecraft mc) {
        System.out.println("Client received: initialization message");
        CwCMod.reset();
        if (playerNameMatches(mc, CwCMod.FIXED_VIEWER))
            CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(0.7, 9, -10, 0, 30, true, true, true, true, true));
        if (playerNameMatches(mc, CwCMod.BUILDER))
            CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(0, 1, 0, 0, 0, true, true, true, true, true));
        if (playerNameMatches(mc, CwCMod.ARCHITECT))
            CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(0, 5, -6, 0, 45, true, true, true, true, true));
        if (playerNameMatches(mc, CwCMod.ORACLE))
            CwCMod.network.sendToServer(new AbsoluteMovementCommandsImplementation.TeleportMessage(0, 5, -6, 0, 45, true, true, true, true, true));
    }
}
