class CrossDatasetEngine:
    def correlate(self, datasets):
        """
        datasets = {
            "sales": df1,
            "marketing": df2,
            "support": df3
        }
        """
        insights = []
        sales = datasets.get("sales")
        marketing = datasets.get("marketing")
        if sales is not None and marketing is not None:
            sales_total = sales["revenue"].sum()
            marketing_total = marketing["spend"].sum()
            if marketing_total > 0:
                ratio = sales_total / marketing_total
                insights.append({
                    "type": "correlation",
                    "message": f"Revenue is {round(ratio,2)}x marketing spend",
                    "confidence": 0.8
                })
        return insights
