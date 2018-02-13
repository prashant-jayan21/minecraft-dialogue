// --------------------------------------------------------------------------------------------------
//  Copyright (c) 2016 Microsoft Corporation
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
//  associated documentation files (the "Software"), to deal in the Software without restriction,
//  including without limitation the rights to use, copy, modify, merge, publish, distribute,
//  sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all copies or
//  substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
//  NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
//  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
//  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
// --------------------------------------------------------------------------------------------------

package com.microsoft.Malmo.MissionHandlers;

import com.google.gson.JsonArray;
import com.google.gson.JsonPrimitive;
import com.microsoft.Malmo.MalmoMod;
import com.microsoft.Malmo.Schemas.*;
import com.microsoft.Malmo.Utils.MinecraftTypeHelper;
import cwc.CwCMod;
import io.netty.buffer.ByteBuf;
import net.minecraft.client.Minecraft;
import net.minecraft.entity.player.EntityPlayerMP;
import net.minecraft.inventory.IInventory;
import net.minecraft.item.ItemStack;
import net.minecraftforge.client.event.ClientChatReceivedEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.player.EntityItemPickupEvent;
import net.minecraftforge.event.world.BlockEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;
import net.minecraftforge.fml.common.network.ByteBufUtils;
import net.minecraftforge.fml.common.network.simpleimpl.IMessage;
import net.minecraftforge.fml.common.network.simpleimpl.IMessageHandler;
import net.minecraftforge.fml.common.network.simpleimpl.MessageContext;

import com.google.gson.JsonObject;
import com.microsoft.Malmo.Utils.JSONWorldDataHelper;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

import java.util.ArrayList;
import java.util.List;

import static com.microsoft.Malmo.MissionHandlers.ObservationFromFullInventoryImplementation.getInventoryJSON;

/**
 * IObservationProducer object that pings out a whole bunch of data.
 * CwCObservation takes care of observations from chat, builder's grid, and the builder's stats (e.g. time alive, distance travelled, etc.).
 */
public class CwCObservationImplementation extends ObservationFromServer
{
    /**
     * Note: identical to {@link ObservationFromGridImplementation#parseParameters(Object)}.
     * @param params the parameter block to parse
     * @return
     */
    @Override
    public boolean parseParameters(Object params) {
        if (params == null || !(params instanceof CwCObservation))
            return false;

        CwCObservation ogparams = (CwCObservation)params;
        this.environs = new ArrayList<ObservationFromGridImplementation.SimpleGridDef>();
        for (GridDefinition gd : ogparams.getGrid())
        {
            ObservationFromGridImplementation.SimpleGridDef sgd = new ObservationFromGridImplementation.SimpleGridDef(
                    gd.getMin().getX().intValue(),
                    gd.getMin().getY().intValue(),
                    gd.getMin().getZ().intValue(),
                    gd.getMax().getX().intValue(),
                    gd.getMax().getY().intValue(),
                    gd.getMax().getZ().intValue(),
                    gd.getName(),
                    gd.isAbsoluteCoords());
            this.environs.add(sgd);
        }
        return true;
    }

    /**
     * Note: identical to {@link com.microsoft.Malmo.MissionHandlers.ObservationFromGridImplementation.GridRequestMessage}.
     */
    public static class CwCRequestMessage extends ObservationFromServer.ObservationRequestMessage
    {
        private List<ObservationFromGridImplementation.SimpleGridDef> environs = null;

        public CwCRequestMessage() { }	// Needed so FML can instantiate our class using reflection.

        public CwCRequestMessage(List<ObservationFromGridImplementation.SimpleGridDef> environs) {
            this.environs = environs;
        }

        @Override
        void restoreState(ByteBuf buf) {
            int numGrids = buf.readInt();
            this.environs = new ArrayList<ObservationFromGridImplementation.SimpleGridDef>();
            for (int i = 0; i < numGrids; i++) {
                ObservationFromGridImplementation.SimpleGridDef sgd = new ObservationFromGridImplementation.SimpleGridDef(buf.readInt(), buf.readInt(), buf.readInt(),
                        buf.readInt(), buf.readInt(), buf.readInt(),
                        ByteBufUtils.readUTF8String(buf),
                        buf.readBoolean());
                this.environs.add(sgd);
            }
        }

        @Override
        void persistState(ByteBuf buf) {
            buf.writeInt(this.environs.size());
            for (ObservationFromGridImplementation.SimpleGridDef sgd : this.environs) {
                buf.writeInt(sgd.xMin);
                buf.writeInt(sgd.yMin);
                buf.writeInt(sgd.zMin);
                buf.writeInt(sgd.xMax);
                buf.writeInt(sgd.yMax);
                buf.writeInt(sgd.zMax);
                ByteBufUtils.writeUTF8String(buf, sgd.name);
                buf.writeBoolean(sgd.absoluteCoords);
            }
        }

        List<ObservationFromGridImplementation.SimpleGridDef> getEnvirons() { return this.environs; }
    }

    /**
     * Note: adapted from {@link com.microsoft.Malmo.MissionHandlers.ObservationFromGridImplementation.GridRequestMessageHandler}.
     * Additional features include recording achievement and position stats normally recorded by {@link com.microsoft.Malmo.Schemas.ObservationFromFullStats}.
     */
    public static class CwCRequestMessageHandler extends ObservationFromServer.ObservationRequestMessageHandler implements IMessageHandler<CwCRequestMessage, IMessage> {
        @Override
        void buildJson(JsonObject json, EntityPlayerMP player, ObservationRequestMessage message) {
            if (message instanceof CwCRequestMessage) {
                JSONWorldDataHelper.buildAchievementStats(json, player, false);
                JSONWorldDataHelper.buildPositionStats(json, player);

                JsonArray arr = new JsonArray();
                getSimplifiedInventoryJSON(arr, player.inventory);
                json.add("BuilderInventory", arr);

                List<ObservationFromGridImplementation.SimpleGridDef> environs = ((CwCRequestMessage)message).getEnvirons();
                if (environs != null) {
                    for (ObservationFromGridImplementation.SimpleGridDef sgd : environs)
                        JSONWorldDataHelper.buildGridData(json, sgd.getEnvirons(), player, sgd.name);
                }
            }
        }

        @Override
        public IMessage onMessage(CwCRequestMessage message, MessageContext ctx) {
            return processMessage(message, ctx);
        }
    }

    public static void getSimplifiedInventoryJSON(JsonArray arr, IInventory inventory) {
        for (int i = 0; i < inventory.getSizeInventory(); i++) {
            ItemStack is = inventory.getStackInSlot(i);
            if (is != null && !is.isEmpty()) {
                JsonObject jobj = new JsonObject();
                DrawItem di = MinecraftTypeHelper.getDrawItemFromItemStack(is);
                String name = di.getType();

                jobj.addProperty("Type", name);
                jobj.addProperty("Index", i);
                jobj.addProperty("Quantity", is.getCount());
                arr.add(jobj);
            }
        }
    }

    private List<ObservationFromGridImplementation.SimpleGridDef> environs = null;
    private ArrayList<String> chatMessagesReceived = new ArrayList<String>(); // list of chat messages received since last JSON was written
    private String lastScreenshotPath = "";                              // screenshot path sent in last JSON
    private boolean actionPerformed = false;                             // marks whether or not a write-triggering action has been performed
    private static int waitTickAfterInit = 0;
    private static boolean initialized = false;

    @Override
    public ObservationRequestMessage createObservationRequestMessage()
    {
        return new CwCRequestMessage(this.environs);
    }

    /**
     * Sends an observation request message to the server upon client tick when a valid action (e.g. chat, pickup, or putdown)
     * has been performed.
     * @param ev Forge client tick event
     */
    @Override
    @SubscribeEvent
    public void onClientTick(TickEvent.ClientTickEvent ev) {
        if (this.missionIsRunning && actionPerformed) {
            // Use the client tick to fire messages to the server to request up-to-date stats.
            // We can then use those stats to fire back to the agent in writeObservationsToJSON.
            ObservationRequestMessage message = createObservationRequestMessage();
            // To make sure only the intended listener receives this message, set the id now:
            message.id = System.identityHashCode(this);
            MalmoMod.network.sendToServer(message);
            actionPerformed = false;
        }
    }

    /**
     * Writes server observations, then chat and screenshot path, to the JSON.
     * @param json JSON object to be written to
     * @param missionInit
     */
    @Override
    public void writeObservationsToJSON(JsonObject json, MissionInit missionInit) {
        super.writeObservationsToJSON(json, missionInit);

        if (!this.chatMessagesReceived.isEmpty()) {
            JsonArray arr = new JsonArray();
            for (String obs : this.chatMessagesReceived)
                arr.add(new JsonPrimitive(obs));
            json.add("Chat", arr);
            this.chatMessagesReceived.clear();
        }

        if (!CwCMod.screenshots.isEmpty() && !CwCMod.screenshots.get(CwCMod.screenshots.size()-1).equals(this.lastScreenshotPath)) {
            this.lastScreenshotPath = CwCMod.screenshots.get(CwCMod.screenshots.size()-1);
            json.add("ScreenshotPath", new JsonPrimitive(this.lastScreenshotPath));
        }
    }

    @Override
    public void prepare(MissionInit missionInit) {
        super.prepare(missionInit);
        reset();
        MinecraftForge.EVENT_BUS.register(this);
    }

    @Override
    public void cleanup() {
        super.cleanup();
        MinecraftForge.EVENT_BUS.unregister(this);
    }

    @SubscribeEvent
    public void onEvent(ClientChatReceivedEvent event) {
        if (event.getType() == 0) {
            this.chatMessagesReceived.add(event.getMessage().getUnformattedText());
            actionPerformed = true;
        }
    }

    @SubscribeEvent
    public void onEvent(EntityItemPickupEvent event) {
        actionPerformed = true;
    }

    @SubscribeEvent
    public void onEvent(BlockEvent.PlaceEvent event) {
        actionPerformed = true;
    }

    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public void onEvent(TickEvent.ClientTickEvent event) {
        if (this.missionIsRunning) {
            if (waitTickAfterInit < 50) waitTickAfterInit++;
            else if (!initialized) {
                if (Minecraft.getMinecraft().player.getName().equals(CwCMod.BUILDER))
                    Minecraft.getMinecraft().player.sendChatMessage("Mission has started.");
                initialized = true;
            }
        }
    }

    private void reset() {
        lastScreenshotPath = "";
        actionPerformed = false;
        waitTickAfterInit = 0;
        initialized = false;
    }
}
