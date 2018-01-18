package cwc;

import com.microsoft.Malmo.MalmoMod;
import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.world.WorldServer;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;
import net.minecraftforge.fml.relauncher.Side;

public class CwCPositionMessageHandler implements IMessageHandler<CwCPositionMessage, IMessage> {

    /**
     * Determines if message is received on the server or the client side and calls their respective message handlers.
     *
     * @param message Position message
     * @param ctx     Message context
     * @return null
     */
    public IMessage onMessage(final CwCPositionMessage message, MessageContext ctx) {
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
            final Minecraft minecraft = Minecraft.getMinecraft();
            minecraft.addScheduledTask(new Runnable() {
                public void run() {
                    processMessageOnClient(message, minecraft);
                }
            });
            return null;
        }
    }

    /**
     * Handles messages received on the server. Processes the message by sending it out to all other connected clients.
     *
     * @param message Position message
     * @param sender  Message sender
     */
    void processMessageOnServer(CwCPositionMessage message, EntityPlayerMP sender) {
        for (EntityPlayerMP player : sender.mcServer.getPlayerList().getPlayers())
            if (!player.getName().equals(sender.getName())) CwCMod.network.sendTo(message, player);
    }

    /**
     * Handles messages received on the client by setting the appropriate "builder's y-coord" field in {@link CwCEventHandler}.
     *
     * @param message   Position message
     * @param minecraft Minecraft client instance
     */
    void processMessageOnClient(CwCPositionMessage message, Minecraft minecraft) {
        if (minecraft.player.getName().equals(MalmoMod.BUILDER))
            CwCMod.network.sendToServer(new CwCPositionMessage(minecraft.player.posY));
        else CwCEventHandler.builderCurrentY = message.y();
    }
}