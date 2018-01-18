package cwc;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

/**
 * Custom message used for sending the y-coordinate of a player's position to the server.
 * @author nrynchn2
 */
public class CwCPositionMessage implements IMessage {
    private double y;

    public CwCPositionMessage() {}
    public CwCPositionMessage(double y) { this.y = y; }

    @Override
    public void fromBytes(ByteBuf buf) { this.y = buf.readDouble(); }

    @Override
    public void toBytes(ByteBuf buf) { buf.writeDouble(this.y); }

    public double y() { return this.y; }
}