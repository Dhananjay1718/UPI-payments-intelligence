// Create a Text parameter named ProjectFolder, e.g. C:\Projects\UPI_Payments_Intelligence
// Create this function as a blank query named LoadCSV.
// A table query then calls: = LoadCSV("fact_monthly")
(TableName as text) as table =>
let
    Source = Csv.Document(
        File.Contents(ProjectFolder & "\data\processed\" & TableName & ".csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    EmptyToNull = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    HasMonth = List.Contains(Table.ColumnNames(EmptyToNull), "month"),
    Dates = if HasMonth then Table.TransformColumnTypes(EmptyToNull, {{"month", type date}}, "en-US") else EmptyToNull,
    NumberColumns = List.Intersect({Table.ColumnNames(Dates), {
        "volume_mn","value_cr","banks_live","daily_volume_mn","avg_ticket_inr",
        "mom_volume","mom_daily_volume","yoy_volume","rolling_3m_volume_mn",
        "six_month_volume","observed_volume_share","td_rate","estimated_td_mn",
        "target_td_rate","effectiveness","scenario_avoided_mn","reported_volume_share",
        "national_volume_mn","national_volume_share","year","month_number","days_in_month"
    }}),
    Typed = Table.TransformColumnTypes(Dates, List.Transform(NumberColumns, each {_, type number}), "en-US")
in
    Typed
