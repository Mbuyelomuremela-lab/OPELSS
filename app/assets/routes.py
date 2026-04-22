from flask import render_template, redirect, url_for, flash, request, send_file, abort, jsonify
from flask_login import login_required, current_user
from app.assets import assets_bp
from app.assets.forms import AssetForm
from app.assets.services import export_assets_excel
from app.extensions import db
from app.models.asset import Asset
from app.models.lab import Lab


@assets_bp.route("/")
@login_required
def index():
    if current_user.role == "Lab Trainee":
        if not current_user.assigned_lab:
            flash("You do not have an assigned lab yet.", "warning")
            return redirect(url_for("dashboard.home"))
        assets = Asset.query.filter_by(lab_id=current_user.assigned_lab_id).order_by(Asset.asset_name).all()
    else:
        assets = Asset.query.order_by(Asset.asset_name).all()

    labs = Lab.query.order_by(Lab.name).all()
    form = AssetForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    if current_user.role == "Lab Trainee":
        form.lab_id.data = current_user.assigned_lab_id

    return render_template("assets/index.html", assets=assets, form=form)


@assets_bp.route("/create", methods=["POST"])
@login_required
def create_asset():
    payload = request.get_json() if request.is_json else None
    form = AssetForm(data=payload) if payload else AssetForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in Lab.query.order_by(Lab.name).all()]
    if form.validate_on_submit():
        if current_user.role == "Lab Trainee" and form.lab_id.data != current_user.assigned_lab_id:
            abort(403)
        asset = Asset(
            asset_name=form.asset_name.data,
            category=form.category.data,
            serial_number=form.serial_number.data,
            status=form.status.data,
            lab_id=form.lab_id.data,
            created_by=current_user.id,
        )
        db.session.add(asset)
        db.session.commit()
        if request.is_json:
            row_html = f"""
            <tr>
              <td>{asset.asset_name}</td>
              <td>{asset.category}</td>
              <td>{asset.serial_number}</td>
              <td><span class=\"badge bg-success\">{asset.status}</span></td>
              <td>{asset.lab.name}</td>
            </tr>
            """
            return jsonify(success=True, message="Asset saved successfully.", row_html=row_html, reload=False, reset=True)
        flash("Asset saved successfully.", "success")
    else:
        errors = "; ".join(
            [f"{field}: {', '.join(messages)}" for field, messages in form.errors.items()]
        )
        if request.is_json:
            return jsonify(success=False, message=f"Unable to save the asset. {errors}"), 400
        flash("Unable to save the asset. Please check the form.", "danger")
    return redirect(url_for("assets.index"))


@assets_bp.route("/export")
@login_required
def export():
    if current_user.role not in ["Admin", "HQ Trainee"]:
        abort(403)
    province_id = request.args.get("province_id", type=int)
    lab_id = request.args.get("lab_id", type=int)
    buffer = export_assets_excel(province_id=province_id, lab_id=lab_id)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="assets_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@assets_bp.route("/<int:asset_id>/update", methods=["POST"])
@login_required
def update_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    form = AssetForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in Lab.query.order_by(Lab.name).all()]
    if form.validate_on_submit():
        if current_user.role == "Lab Trainee" and asset.lab_id != current_user.assigned_lab_id:
            abort(403)
        if current_user.role == "Lab Trainee" and form.lab_id.data != current_user.assigned_lab_id:
            abort(403)
        asset.asset_name = form.asset_name.data
        asset.category = form.category.data
        asset.serial_number = form.serial_number.data
        asset.status = form.status.data
        asset.lab_id = form.lab_id.data
        db.session.commit()
        flash("Asset updated successfully.", "success")
    else:
        flash("Unable to update asset. Please review the form.", "danger")
    return redirect(url_for("assets.index"))


@assets_bp.route("/<int:asset_id>/delete", methods=["POST"])
@login_required
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    if current_user.role == "Lab Trainee" and asset.lab_id != current_user.assigned_lab_id:
        abort(403)
    db.session.delete(asset)
    db.session.commit()
    flash("Asset deleted successfully.", "success")
    return redirect(url_for("assets.index"))
