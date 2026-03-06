import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface ChartRendererProps {
  chart: any;
  onItemClick?: (itemData: any) => void;
}

// Helper function to make chart labels more readable
const formatChartLabel = (label: string): string => {
  // Remove function calls like SUM(), COUNT(), etc.
  let formatted = label.replace(/^(SUM|COUNT|AVG|MAX|MIN|YEAR|MONTH|DAY)\(/i, '').replace(/\)$/, '');
  // Remove table aliases like "soh.", "c.", "p."
  formatted = formatted.replace(/^[a-z]+\./i, '');
  // Convert to Title Case
  formatted = formatted
    .replace(/([A-Z])/g, ' $1') // Add space before capitals
    .replace(/(_|-)/g, ' ') // Replace underscores and hyphens with spaces
    .trim()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
  return formatted;
};

const ChartRenderer: React.FC<ChartRendererProps> = ({ chart, onItemClick }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!containerRef.current || !chart) return;

    // Initialize chart
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(containerRef.current);
    }

    const option = buildChartOption(chart);
    if (option && Object.keys(option).length > 0) {
      chartInstance.current.setOption(option);
    }

    // Add click handler
    if (onItemClick) {
      chartInstance.current.off('click');
      chartInstance.current.on('click', (params: any) => {
        onItemClick({
          name: params.name,
          value: params.value,
          seriesName: params.seriesName,
          dataIndex: params.dataIndex,
          chartType: chart.type,
          chartTitle: chart.title,
        });
      });
    }

    // Handle resize
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [chart, onItemClick]);

  const buildChartOption = (chartData: any) => {
    if (!chartData) return {};
    
    switch (chartData.type) {
      case 'bar':
        return {
          title: {
            text: chartData.title,
            left: 'center',
            textStyle: {
              color: 'var(--text-primary)',
              fontSize: 14,
              fontWeight: 600,
            },
          },
          tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            borderColor: 'var(--border)',
            textStyle: { color: '#fff' },
          },
          grid: {
            left: '10%',
            right: '10%',
            bottom: '25%',
            top: '15%',
            containLabel: true,
          },
          xAxis: {
            type: 'category',
            data: chartData.xAxis.data,
            axisLabel: {
              color: 'var(--text-secondary)',
              fontSize: 12,
              interval: 0,
              rotate: 45,
            },
            axisLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
          },
          yAxis: {
            type: 'value',
            name: formatChartLabel(chartData.yAxis.name),
            axisLabel: {
              color: 'var(--text-secondary)',
              fontSize: 12,
            },
            axisLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
            splitLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
          },
          series: chartData.series.map((s: any, idx: number) => ({
            name: s.name,
            data: s.data,
            type: 'bar',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#3b82f6' },
                { offset: 1, color: '#06b6d4' },
              ]),
            },
            emphasis: {
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#60a5fa' },
                  { offset: 1, color: '#22d3ee' },
                ]),
              },
            },
          })),
        };

      case 'pie':
        const colors = ['#3b82f6', '#06b6d4', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];
        const pieData = Array.isArray(chartData.data) ? chartData.data.map((item: any) => {
          // Handle both object format {value, name} and plain values
          if (typeof item === 'object' && item !== null && 'value' in item) {
            return {
              value: Number(item.value) || 0,
              name: item.name || ''
            };
          }
          return item;
        }) : [];
        return {
          title: {
            text: chartData.title,
            left: 'center',
            textStyle: {
              color: 'var(--text-primary)',
              fontSize: 14,
              fontWeight: 600,
            },
          },
          color: colors,
          tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            borderColor: 'var(--border)',
            textStyle: { color: '#fff' },
            formatter: '{b}: {c} ({d}%)',
          },
          series: [
            {
              name: chartData.title,
              type: 'pie',
              radius: ['25%', '65%'],
              center: ['50%', '50%'],
              data: pieData,
              itemStyle: {
                borderRadius: 4,
                borderColor: 'var(--bg-secondary)',
                borderWidth: 2,
              },
              label: {
                color: 'var(--text-secondary)',
                fontSize: 11,
              },
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)',
                },
              },
            },
          ],
        };

      case 'line':
        return {
          title: {
            text: chartData.title,
            left: 'center',
            textStyle: {
              color: 'var(--text-primary)',
              fontSize: 14,
              fontWeight: 600,
            },
          },
          tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            borderColor: 'var(--border)',
            textStyle: { color: '#fff' },
          },
          grid: {
            left: '10%',
            right: '10%',
            bottom: '25%',
            top: '15%',
            containLabel: true,
          },
          xAxis: {
            type: 'category',
            data: chartData.xAxis.data,
            axisLabel: {
              color: 'var(--text-secondary)',
              fontSize: 12,
              interval: 0,
              rotate: 45,
            },
            axisLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
          },
          yAxis: {
            type: 'value',
            name: formatChartLabel(chartData.yAxis.name),
            axisLabel: {
              color: 'var(--text-secondary)',
              fontSize: 12,
            },
            axisLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
            splitLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
          },
          series: chartData.series.map((s: any) => ({
            name: s.name,
            data: s.data,
            type: 'line',
            smooth: true,
            itemStyle: {
              color: '#3b82f6',
            },
            lineStyle: {
              color: '#3b82f6',
              width: 2,
            },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                { offset: 1, color: 'rgba(59, 130, 246, 0)' },
              ]),
            },
          })),
        };

      case 'scatter':
        return {
          title: {
            text: chartData.title,
            left: 'center',
            textStyle: {
              color: 'var(--text-primary)',
              fontSize: 14,
              fontWeight: 600,
            },
          },
          tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            borderColor: 'var(--border)',
            textStyle: { color: '#fff' },
          },
          grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '15%',
            containLabel: true,
          },
          xAxis: {
            type: 'value',
            axisLabel: {
              color: 'var(--text-secondary)',
              fontSize: 12,
            },
            axisLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
            splitLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              color: 'var(--text-secondary)',
              fontSize: 12,
            },
            axisLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
            splitLine: {
              lineStyle: {
                color: 'var(--border)',
              },
            },
          },
          series: chartData.series.map((s: any) => ({
            name: s.name,
            data: s.data,
            type: 'scatter',
            symbolSize: 8,
            itemStyle: {
              color: '#3b82f6',
              opacity: 0.6,
            },
            emphasis: {
              itemStyle: {
                color: '#06b6d4',
                opacity: 1,
              },
            },
          })),
        };
    }
  };

  const renderDataTable = () => {
    if (!chart) return null;

    switch (chart.type) {
      case 'bar':
        return (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>Chart Data</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'var(--card-bg, #1a202c)',
                border: '1px solid var(--border-color, #2d3748)',
                borderRadius: '8px',
                overflow: 'hidden'
              }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--hover-bg, #2d3748)' }}>
                    <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: 600, borderBottom: '1px solid var(--border-color, #2d3748)' }}>Name</th>
                    <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-secondary)', fontWeight: 600, borderBottom: '1px solid var(--border-color, #2d3748)' }}>Value</th>
                  </tr>
                </thead>
                <tbody>
                  {chart.xAxis?.data?.map((name: string, idx: number) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-color, #2d3748)' }}>
                      <td style={{ padding: '12px', color: 'var(--text-primary)' }}>{name}</td>
                      <td style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 500 }}>
                        {chart.series[0]?.data[idx]?.toLocaleString?.() || chart.series[0]?.data[idx]}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      case 'pie':
        return (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>Chart Data</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'var(--card-bg, #1a202c)',
                border: '1px solid var(--border-color, #2d3748)',
                borderRadius: '8px',
                overflow: 'hidden'
              }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--hover-bg, #2d3748)' }}>
                    <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: 600, borderBottom: '1px solid var(--border-color, #2d3748)' }}>Category</th>
                    <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-secondary)', fontWeight: 600, borderBottom: '1px solid var(--border-color, #2d3748)' }}>Value</th>
                    <th style={{ padding: '12px', textAlign: 'right', color: 'var(--text-secondary)', fontWeight: 600, borderBottom: '1px solid var(--border-color, #2d3748)' }}>Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {chart.data?.map((item: any, idx: number) => {
                    const total = chart.data.reduce((sum: number, d: any) => sum + (typeof d === 'object' ? d.value : d), 0);
                    const value = typeof item === 'object' ? item.value : item;
                    const name = typeof item === 'object' ? item.name : `Item ${idx + 1}`;
                    const percentage = ((value / total) * 100).toFixed(1);
                    return (
                      <tr key={idx} style={{ borderBottom: '1px solid var(--border-color, #2d3748)' }}>
                        <td style={{ padding: '12px', color: 'var(--text-primary)' }}>{name}</td>
                        <td style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 500 }}>
                          {value.toLocaleString?.() || value}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 500 }}>
                          {percentage}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        );

      case 'line':
        return (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>Chart Data</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                backgroundColor: 'var(--card-bg, #1a202c)',
                border: '1px solid var(--border-color, #2d3748)',
                borderRadius: '8px',
                overflow: 'hidden'
              }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--hover-bg, #2d3748)' }}>
                    <th style={{ padding: '12px', textAlign: 'left', color: 'var(--text-secondary)', fontWeight: 600, borderBottom: '1px solid var(--border-color, #2d3748)' }}>X-Axis</th>
                    {chart.series?.map((s: any, idx: number) => (
                      <th key={idx} style={{ padding: '12px', textAlign: 'right', color: 'var(--text-secondary)', fontWeight: 600, borderBottom: '1px solid var(--border-color, #2d3748)' }}>
                        {s.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {chart.xAxis?.data?.map((xVal: string, idx: number) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-color, #2d3748)' }}>
                      <td style={{ padding: '12px', color: 'var(--text-primary)' }}>{xVal}</td>
                      {chart.series?.map((s: any, sIdx: number) => (
                        <td key={sIdx} style={{ padding: '12px', textAlign: 'right', color: 'var(--text-primary)', fontWeight: 500 }}>
                          {s.data[idx]?.toLocaleString?.() || s.data[idx]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div>
      <div ref={containerRef} style={{ width: '100%', height: '400px' }} />
      {renderDataTable()}
    </div>
  );
};

export default ChartRenderer;
