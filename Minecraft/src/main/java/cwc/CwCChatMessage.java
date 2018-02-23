package cwc;

import io.netty.buffer.ByteBuf;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;

public class CwCChatMessage implements IMessage {
    private boolean chatting;

    public CwCChatMessage() {}
    public CwCChatMessage(boolean chatting) { this.chatting = chatting; }

    @Override
    public void fromBytes(ByteBuf buf) { this.chatting = buf.readBoolean(); }

    @Override
    public void toBytes(ByteBuf buf) { buf.writeBoolean(this.chatting); }

    public boolean chatting() { return this.chatting; }
}
