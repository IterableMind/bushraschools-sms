"""
Defines routes related to a teacher with no admin resposibilities.
"""
from flask import render_template, url_for
from . import teachr_bp


@teachr_bp.route('/dashboard')
def dashboard():
  return render_template('teach_dashboard.html')