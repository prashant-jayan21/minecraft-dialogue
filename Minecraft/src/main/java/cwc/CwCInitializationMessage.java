package cwc;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

/**
 * Custom message used for quitting out of missions.
 * @author nrynchn2
 */
public class CwCInitializationMessage implements IMessage {

    public CwCInitializationMessage() {}

    @Override
    public void fromBytes(ByteBuf buf) { }

    @Override
    public void toBytes(ByteBuf buf) { }
}
