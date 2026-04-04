export const vehicles = [
  {
    id: "VEH001", name: "Honda City", owner: "Sarah Khan",
    status: "critical", mileage: 52000,
    sensors: { brakeTemp: 85, oilPressure: 38, engineTemp: 92, brakeFluid: 40 }
  },
  {
    id: "VEH002", name: "Toyota Innova", owner: "Rahul Singh",
    status: "warning", mileage: 38000,
    sensors: { brakeTemp: 72, oilPressure: 42, engineTemp: 88, brakeFluid: 65 }
  },
  {
    id: "VEH003", name: "Maruti Swift", owner: "Priya Patel",
    status: "healthy", mileage: 15000,
    sensors: { brakeTemp: 62, oilPressure: 45, engineTemp: 85, brakeFluid: 90 }
  },
  {
    id: "VEH004", name: "Hyundai Creta", owner: "Amit Sharma",
    status: "healthy", mileage: 22000,
    sensors: { brakeTemp: 65, oilPressure: 44, engineTemp: 86, brakeFluid: 80 }
  },
  {
    id: "VEH005", name: "Tata Nexon", owner: "Neha Gupta",
    status: "healthy", mileage: 8000,
    sensors: { brakeTemp: 60, oilPressure: 46, engineTemp: 83, brakeFluid: 95 }
  },
  {
    id: "VEH006", name: "Mahindra XUV", owner: "Raj Mehta",
    status: "warning", mileage: 45000,
    sensors: { brakeTemp: 70, oilPressure: 40, engineTemp: 90, brakeFluid: 55 }
  },
  {
    id: "VEH007", name: "Ford EcoSport", owner: "Anita Verma",
    status: "healthy", mileage: 12000,
    sensors: { brakeTemp: 63, oilPressure: 45, engineTemp: 84, brakeFluid: 88 }
  },
  {
    id: "VEH008", name: "VW Polo", owner: "Vijay Kumar",
    status: "healthy", mileage: 28000,
    sensors: { brakeTemp: 66, oilPressure: 43, engineTemp: 87, brakeFluid: 75 }
  },
  {
    id: "VEH009", name: "Renault Kwid", owner: "Kavita Joshi",
    status: "healthy", mileage: 5000,
    sensors: { brakeTemp: 58, oilPressure: 47, engineTemp: 82, brakeFluid: 98 }
  },
  {
    id: "VEH010", name: "Nissan Magnite", owner: "Suresh Nair",
    status: "critical", mileage: 55000,
    sensors: { brakeTemp: 81, oilPressure: 35, engineTemp: 95, brakeFluid: 35 }
  },
];

export const predictions = [
  {
    vehicleId: "VEH001", component: "Brake Pads",
    daysUntilFailure: 7, probability: 85, priority: "CRITICAL",
    factors: ["Brake temp 30% above normal", "Brake fluid at 40%"]
  },
  {
    vehicleId: "VEH010", component: "Coolant System",
    daysUntilFailure: 10, probability: 72, priority: "CRITICAL",
    factors: ["Coolant level dropping", "Engine temp elevated"]
  },
  {
    vehicleId: "VEH002", component: "Oil Filter",
    daysUntilFailure: 14, probability: 65, priority: "WARNING",
    factors: ["Oil service overdue 2 months"]
  },
  {
    vehicleId: "VEH006", component: "Battery",
    daysUntilFailure: 21, probability: 55, priority: "WARNING",
    factors: ["Battery age 3 years", "Voltage fluctuating"]
  },
];

export const agents = [
  { id: "master",        name: "Master Agent",   icon: "🧠", status: "active"     },
  { id: "data",          name: "Data Analysis",  icon: "📊", status: "processing" },
  { id: "diagnosis",     name: "Diagnosis",      icon: "🔬", status: "idle"       },
  { id: "engagement",    name: "Engagement",     icon: "📞", status: "idle"       },
  { id: "scheduling",    name: "Scheduling",     icon: "📅", status: "idle"       },
  { id: "feedback",      name: "Feedback",       icon: "⭐", status: "idle"       },
  { id: "manufacturing", name: "Manufacturing",  icon: "🏭", status: "idle"       },
];

export const dashStats = {
  total: 10,
  alerts: 3,
  healthy: 6,
  accuracy: 92,
  moneySaved: 45000
};