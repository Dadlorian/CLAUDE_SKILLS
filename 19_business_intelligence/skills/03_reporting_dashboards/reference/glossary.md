# Dashboard Design Glossary

## A

**Accessibility**
Design practice ensuring dashboards are usable by people with disabilities, including visual, motor, and cognitive impairments. See WCAG 2.1.

**Aggregation**
Combining detailed data into summary form (e.g., daily sales → monthly sales). Critical for dashboard performance.

**ARIA (Accessible Rich Internet Applications)**
Set of attributes that make web content and dashboards more accessible to people using assistive technologies.

**Auto-Refresh**
Automatic update of dashboard data at specified intervals without user interaction.

## B

**Baseline**
Reference point for comparison (e.g., target, previous period, industry benchmark).

**Benchmark**
Standard or point of reference against which things may be compared. Essential for context in dashboards.

**Breadcrumb**
Navigation element showing user's location in hierarchy (e.g., Home > Sales > North Region).

**Bullet Chart**
Stephen Few's space-efficient chart showing performance against target with qualitative ranges. Superior alternative to gauge charts.

## C

**Chartjunk**
Non-data elements that don't add information (Tufte): 3D effects, excessive gridlines, decorative fills, shadows, backgrounds.

**Cognitive Load**
Mental effort required to use dashboard. Good design minimizes cognitive load.

**Cohort Analysis**
Grouping users/customers by shared characteristic (e.g., signup month) to analyze behavior over time.

**Cross-Filtering**
Selecting data in one visualization filters data in others. Powerful for exploration.

## D

**Dashboard**
Single-screen information display combining multiple visualizations and metrics for monitoring and decision-making.

**Data Density**
Amount of information per unit of space. Tufte advocates for high data density (with clarity).

**Data-Ink Ratio**
Tufte's principle: proportion of ink devoted to displaying data. Higher is better.

**Drill-Down**
Navigation from summary to detail (e.g., revenue → by region → by product → by customer).

**Diverging Palette**
Color scheme with two distinct colors (e.g., red and blue) meeting at neutral midpoint. Use for data with meaningful center (above/below target).

## E

**Executive Dashboard**
High-level dashboard for senior leadership showing strategic KPIs. Typically 5-7 key metrics, minimal detail.

**Extract**
Snapshot of data stored locally for fast query performance. Alternative to live database connection.

## F

**F-Pattern**
Reading pattern where eyes scan horizontally at top, then down left side, then shorter horizontal scan. Informs dashboard layout.

**Filter**
Control allowing users to narrow data displayed (e.g., date range, region, product category).

**Focus + Context**
Design pattern showing overview (context) and detail (focus) simultaneously.

## G

**Gauge Chart**
Circular chart resembling speedometer. Stephen Few recommends avoiding due to space inefficiency. Use bullet charts instead.

**Gestalt Principles**
Psychological principles of visual perception (proximity, similarity, closure). Applied to group related dashboard elements.

**Grayscale First**
Knaflic's technique: design dashboard in grayscale, then add color only for emphasis.

**Gridlines**
Reference lines on charts. Tufte recommends minimal or no gridlines to reduce chartjunk.

## H

**Heatmap**
Visualization using color intensity to represent values in matrix format.

**Hierarchy (Visual)**
Arrangement of elements by importance, guiding viewer's eye through dashboard logically.

## I

**Information Scent**
Stephen Few's concept: users can quickly recognize whether dashboard contains information they need.

**Interactivity**
Dashboard elements users can manipulate (filters, drill-downs, hover tooltips).

## K

**Key Performance Indicator (KPI)**
Measurable value demonstrating how effectively organization achieves business objectives.

**Knaflic, Cole Nussbaumer**
Author of "Storytelling with Data". Emphasizes narrative, eliminating clutter, and focusing attention.

## L

**Layout**
Arrangement of dashboard elements on screen. Should follow reading patterns and visual hierarchy.

**Legend**
Key explaining chart symbols/colors. Few/Tufte recommend direct labeling instead to reduce eye travel.

**Live Connection**
Real-time query to database. Provides current data but slower than extracts.

**LookML**
Looker Modeling Language. Defines data model and business logic in Looker.

## M

**Materialized View**
Pre-computed database view storing query results. Improves dashboard performance dramatically.

**Mobile-First**
Design approach starting with mobile constraints, then enhancing for larger screens.

**Mock-up**
Visual representation of dashboard design before implementation. Essential for gathering feedback.

## N

**Narrative**
Story told by dashboard: setup (where we are) → insight (what's happening) → action (what to do).

**Net Promoter Score (NPS)**
Customer loyalty metric. Scale -100 to +100. Common dashboard KPI.

## O

**Operational Dashboard**
Real-time monitoring dashboard for day-to-day operations. Often alert-driven with 10-15 key metrics.

**Outlier**
Data point significantly different from others. Should be highlighted and explained in dashboards.

## P

**Palette**
Set of colors used in dashboard. Should be limited (≤7 colors), accessible, and purposeful.

**PDT (Persistent Derived Table)**
Looker's materialized table written back to database for performance.

**Pie Chart**
Circular chart showing parts of whole. Few/Tufte recommend avoiding (hard to compare angles). Use bar charts instead.

**Pre-Attentive Attributes**
Visual properties processed unconsciously in <500ms: color, size, position. Use to guide attention.

**Progressive Disclosure**
Revealing detail gradually. Start with summary, drill down for more information.

## Q

**Qualitative Palette**
Colors for distinct categories (no inherent order). Use color-blind safe combinations.

**Query Performance**
Speed of database queries. Critical for dashboard usability. Target: <3 seconds.

## R

**Refresh Rate**
Frequency of data updates. Balance currency needs with performance.

**Responsive Design**
Layout adapts to different screen sizes (desktop, tablet, mobile).

**Row-Level Security (RLS)**
Data access control showing users only data they're authorized to see.

## S

**Semantic Layer**
Business logic layer defining metrics consistently across organization. Prevents conflicting definitions.

**Sequential Palette**
Color scheme from light to dark representing ordered data (low to high values).

**Small Multiples**
Tufte's technique: series of similar charts with same scale enabling easy comparison.

**Sparkline**
Tufte's word-sized graphic showing trend. Typically embedded in text or tables without axes.

**Stacked Bar**
Bar chart showing parts of whole. Each bar divided into segments. Use for 2-4 components maximum.

**Storytelling**
Knaflic's framework: using data and visuals to tell compelling narrative that drives action.

## T

**Tactical Dashboard**
Department-level dashboard balancing overview and detail. Typically 10-20 metrics.

**Treemap**
Rectangular chart showing hierarchical part-to-whole. Space-efficient but hard for precise comparison.

**Tufte, Edward**
Author of "The Visual Display of Quantitative Information". Pioneer of data visualization principles (data-ink ratio, chartjunk, small multiples).

## U

**User Story**
Statement defining who needs dashboard, what they need, and why. Format: "As a [role], I want [goal] so that [benefit]."

## V

**Visual Hierarchy**
Organization of elements by importance using size, color, position, and typography.

**Viz (Visualization)**
Short for data visualization. Chart, graph, or graphic representation of data.

## W

**Waterfall Chart**
Shows cumulative effect of sequential positive/negative values. Useful for revenue/cost breakdowns.

**WCAG (Web Content Accessibility Guidelines)**
International accessibility standards. Level AA is common target for dashboards.

**White Space**
Empty space around elements. Not wasted space—helps create visual hierarchy and reduces clutter.

## Z

**Z-Pattern**
Reading pattern for page scanning: top-left → top-right → diagonal → bottom-left → bottom-right. Informs layout design.

---

## Dashboard Types by Purpose

**Executive Dashboard**: Strategic KPIs for leadership (5-7 metrics)
**Operational Dashboard**: Real-time monitoring (10-15 metrics)
**Analytical Dashboard**: Deep exploration (15-20 metrics, heavy interactivity)
**Tactical Dashboard**: Department-specific (10-15 metrics)

## Common Acronyms

- **ARR**: Annual Recurring Revenue
- **CAC**: Customer Acquisition Cost
- **CSAT**: Customer Satisfaction Score
- **DAU**: Daily Active Users
- **DAX**: Data Analysis Expressions (Power BI)
- **EBITDA**: Earnings Before Interest, Taxes, Depreciation, Amortization
- **ETL**: Extract, Transform, Load
- **LTV**: Lifetime Value
- **MAU**: Monthly Active Users
- **MoM**: Month over Month
- **MRR**: Monthly Recurring Revenue
- **NPS**: Net Promoter Score
- **NRR**: Net Revenue Retention
- **QoQ**: Quarter over Quarter
- **SLA**: Service Level Agreement
- **YoY**: Year over Year

---

## References

**Few, Stephen**
Information Dashboard Design, Show Me the Numbers, Now You See It

**Tufte, Edward**
The Visual Display of Quantitative Information, Envisioning Information, Visual Explanations, Beautiful Evidence

**Knaflic, Cole Nussbaumer**
Storytelling with Data, Storytelling with Data: Let's Practice!

**Other Key Sources**
- Nielsen Norman Group (UX research)
- WCAG 2.1 (Accessibility standards)
- Colorbrewer 2.0 (Color palettes)
- The Economist, FiveThirtyEight (Data journalism examples)
