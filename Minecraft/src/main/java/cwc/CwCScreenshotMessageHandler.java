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

public class CwCScreenshotMessageHandler implements IMessageHandler<CwCScreenshotMessage, IMessage> {
    public IMessage onMessage(final CwCScreenshotMessage message, MessageContext ctx) {
        if (ctx.side == Side.SERVER) {
            System.out.println("A message has been received.");
            final EntityPlayerMP sender = ctx.getServerHandler().playerEntity;
            if (ctx.getServerHandler().playerEntity == null) return null;

            System.out.println("Sending message to all clients...");
            final WorldServer pws = sender.getServerWorld();
            pws.addScheduledTask(new Runnable() {
                public void run() { processMessageOnServer(message, sender); }
            });

            return null;
        }

        else {
            final Minecraft minecraft = Minecraft.getMinecraft();
            minecraft.addScheduledTask(new Runnable() {
                public void run() { processMessageOnClient(message); }
            });
            return null;
        }
    }

    void processMessageOnServer(CwCScreenshotMessage message, EntityPlayerMP sender) {
        for (EntityPlayerMP player : sender.mcServer.getPlayerList().getPlayers())
            CwCMod.network.sendTo(message, player);
    }

    void processMessageOnClient(CwCScreenshotMessage message) {
        if (message.getType() == CwCScreenshotEventType.PICKUP)
            CwCEventHandler.pickedUpBlock = true;
        else if (message.getType() == CwCScreenshotEventType.PUTDOWN)
            CwCEventHandler.placedBlock = true;
    }
}
