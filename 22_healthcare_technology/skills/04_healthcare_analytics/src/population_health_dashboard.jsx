// Population Health Dashboard Component (React)
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PopulationHealthDashboard = () => {
  const [kpis, setKpis] = useState({
    totalPopulation: 45000,
    qualityScore: 82.5,
    admitsPerK: 85,
    costPMPM: 450
  });

  const [qualityTrend, setQualityTrend] = useState([
    { month: 'Jan', score: 78 }, { month: 'Feb', score: 79 },
    { month: 'Mar', score: 80 }, { month: 'Apr', score: 81 },
    { month: 'May', score: 82 }, { month: 'Jun', score: 82.5 }
  ]);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Population Health Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader><CardTitle>Total Population</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{kpis.totalPopulation.toLocaleString()}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Quality Score</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{kpis.qualityScore}</div>
            <div className="text-sm text-green-600">▲ 2.3 pts YoY</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>IP Admits per 1000</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{kpis.admitsPerK}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Cost PMPM</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">${kpis.costPMPM}</div>
          </CardContent>
        </Card>
      </div>

      {/* Quality Trend Chart */}
      <Card>
        <CardHeader><CardTitle>Quality Score Trend</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={qualityTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis domain={[70, 90]} />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default PopulationHealthDashboard;
