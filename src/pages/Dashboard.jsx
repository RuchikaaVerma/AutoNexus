import { useState } from "react";
import { dashStats, vehicles, predictions, agents }
  from "../data/mockData";

import StatsRow       from "../components/StatsRow";
import VehicleGrid    from "../components/VehicleGrid";
import SensorGauges   from "../components/SensorGauges";
import AgentPanel     from "../components/AgentPanel";
import PredictionList from "../components/PredictionList";
import ChatViewer     from "../components/ChatViewer";
import DemoMode       from "../components/DemoMode";

export default function Dashboard() {
  // Selected vehicle track karo — default pehli critical
  const [selectedVehicle, setSelectedVehicle] = useState(
    vehicles.find(v => v.status === "critical") || vehicles[0]
  );

  // Demo mode mein active agent
  const [activeAgent, setActiveAgent] = useState(null);

  return (
    <div className="pt-16 min-h-screen bg-gray-950 p-5">

      {/* PAGE TITLE */}
      <div className="mb-5">
        <p className="text-xs text-white/30 tracking-widest uppercase mb-1">
          Overview
        </p>
        <h1 className="text-2xl font-bold text-white">
          Fleet Dashboard
        </h1>
      </div>

      {/* Stats */}
      <StatsRow stats={dashStats} />

      {/* Main Layout */}
      <div className="grid grid-cols-12 gap-4">

        {/* LEFT — Sensors change honge click pe */}
        <div className="col-span-3 flex flex-col gap-4">
          <SensorGauges vehicle={selectedVehicle} />
          <PredictionList predictions={predictions} />
        </div>

        {/* CENTER — onClick pass karo */}
        <div className="col-span-6">
          <VehicleGrid
            vehicles={vehicles}
            selectedId={selectedVehicle.id}
            onSelect={setSelectedVehicle}
          />
        </div>

        {/* RIGHT */}
        <div className="col-span-3 flex flex-col gap-4">
          <AgentPanel
            agents={agents}
            activeAgent={activeAgent}
          />
          <ChatViewer />
        </div>

      </div>

      {/* Demo Button */}
      <DemoMode onAgentChange={setActiveAgent} />

    </div>
  );
}