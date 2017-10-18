package cwc;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.ByteBufUtils;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

public class CwCStateMessage implements IMessage {
    private String state;

    public CwCStateMessage() {}
    public CwCStateMessage(CwCState state) { this.state = state.name(); }

    @Override
    public void fromBytes(ByteBuf buf) { this.state = ByteBufUtils.readUTF8String(buf); }

    @Override
    public void toBytes(ByteBuf buf) { ByteBufUtils.writeUTF8String(buf, this.state); }

    public String getState() { return this.state; }
}
