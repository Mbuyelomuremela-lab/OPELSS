from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from app.models.asset import Asset
from app.models.lab import Lab


def export_assets_excel(province_id=None, lab_id=None):
    query = Asset.query.join(Lab)
    if lab_id:
        query = query.filter(Asset.lab_id == lab_id)
    if province_id:
        query = query.filter(Lab.province_id == province_id)

    assets = query.order_by(Asset.asset_name).all()
    workbook = Workbook()
    raw = workbook.active
    raw.title = "Assets"
    headers = ["Asset Name", "Category", "Serial Number", "Status", "Lab", "Province"]
    raw.append(headers)

    for asset in assets:
        raw.append([
            asset.asset_name,
            asset.category,
            asset.serial_number,
            asset.status,
            asset.lab.name if asset.lab else "",
            asset.lab.province.name if asset.lab and asset.lab.province else "",
        ])

    summary = workbook.create_sheet(title="Summary")
    summary["A1"] = "Asset Export Summary"
    summary["A1"].font = Font(bold=True)
    summary["A2"] = "Total Assets"
    summary["B2"] = len(assets)
    summary["A2"].alignment = Alignment(horizontal="left")
    summary["B2"].alignment = Alignment(horizontal="center")

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer
