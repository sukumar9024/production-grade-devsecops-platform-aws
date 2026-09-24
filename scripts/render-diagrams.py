#!/usr/bin/env python3
"""Render architecture PNGs. Optional tooling: pip install Pillow==12.3.0."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "diagrams"
OUT.mkdir(exist_ok=True)


def font(size, bold=False):
    candidates = [f"/System/Library/Fonts/Supplemental/Arial{' Bold' if bold else ''}.ttf",
                  f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf"]
    for name in candidates:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default(size=size)


def render(filename, title, subtitle, nodes, edges):
    image = Image.new("RGB", (1500, 950), "#f5f7fb")
    draw = ImageDraw.Draw(image)
    draw.text((65, 50), title, fill="#12304a", font=font(40, True))
    draw.text((65, 112), subtitle, fill="#4a6178", font=font(22))
    for start, end in edges:
        a, b = nodes[start], nodes[end]
        ax, ay, bx, by = a[0]+170, a[1]+65, b[0]+170, b[1]+65
        angle = math.atan2(by-ay, bx-ax)
        dx, dy = math.cos(angle), math.sin(angle)
        offset = min(170 / max(abs(dx), .01), 65 / max(abs(dy), .01))
        offset_b = min(170 / max(abs(dx), .01), 65 / max(abs(dy), .01))
        x1,y1,x2,y2=ax+offset*dx,ay+offset*dy,bx-offset_b*dx,by-offset_b*dy
        draw.line((x1,y1,x2,y2),fill="#7290a9",width=4)
        draw.polygon([(x2,y2),(x2-16*dx+7*dy,y2-16*dy-7*dx),(x2-16*dx-7*dy,y2-16*dy+7*dx)],fill="#7290a9")
    for x,y,title,body in nodes:
        draw.rounded_rectangle((x,y,x+340,y+130),radius=15,fill="white",outline="#aac4d8",width=2)
        draw.text((x+22,y+20),title,font=font(24,True),fill="#12304a")
        draw.multiline_text((x+22,y+59),body,font=font(19),fill="#4a6178",spacing=7)
    draw.text((65,900),"SecureOps • Architecture design • Live AWS acceptance remains pending",font=font(19),fill="#526a80")
    image.save(OUT/filename)


render('01-aws-architecture.png','AWS platform','Public HTTPS ingress, private application and data tiers',[
 (65,210,'Users','Browser / HTTPS'),(580,210,'Route53 + ACM + ALB','DNS, certificate, HTTP redirect'),
 (580,460,'Private application EC2','Nginx gateway → active slot\nReact + FastAPI containers'),
 (65,710,'RDS PostgreSQL','Private • TLS • backups'),(580,710,'ElastiCache Redis','Private • AUTH • TLS'),
 (1095,710,'S3 + Secrets Manager','Encrypted objects and secrets'),(1095,460,'Managed OpenSearch','Central application / host logs')],[(0,1),(1,2),(2,3),(2,4),(2,5),(2,6)])
render('02-network-architecture.png','Network boundaries','Two availability zones; application and database instances have no public IP',[
 (65,220,'Internet Gateway','Public ingress / egress'),(580,220,'Public subnets • AZ A/B','ALB + NAT gateways'),
 (580,465,'Private app • AZ A/B','EC2 • ALB-only port 8080\nOutbound HTTPS through NAT'),
 (65,710,'Database subnets','No default Internet route\n5432 from app security group'),
 (1095,710,'Cache subnets','No default Internet route\n6379 from app security group'),
 (1095,220,'Systems Manager','Administrative sessions\nNo public SSH')],[(0,1),(1,2),(2,3),(2,4),(5,2)])
render('03-cicd-pipeline.png','Release pipeline','Production promotion requires main, staging verification and a release-manager approval',[
 (65,210,'Git → Jenkins','Checkout • lint • unit/API tests'),(580,210,'Security gates','Semgrep • dependencies • IaC\nGit secrets • Trivy images'),
 (1095,210,'ECR','Immutable Git SHA tags\nDeploy by SHA256 digest'),(1095,465,'Staging','Ansible / SSM deployment\nAuthenticated smoke + ZAP'),
 (580,710,'Production approval','main branch only\nRecorded Jenkins approval'),(65,710,'Production rollout','Candidate → smoke → gateway\nVerify ALB or roll back')],[(0,1),(1,2),(2,3),(3,4),(4,5)])
render('04-observability.png','Observability','Host-local metrics and dashboards; centralized logs in private OpenSearch',[
 (65,210,'Metrics sources','FastAPI / node / cAdvisor\nReadiness HTTP probe'),(580,210,'Prometheus','15-second scraping\n15-day metrics retention'),
 (1095,210,'Grafana','Infrastructure / app / release\nPrivate access through SSM'),(580,465,'Alertmanager','Availability / CPU / RAM / disk\nErrors / deployment failure'),
 (1095,465,'Slack + AWS SNS','Configured recipients\nDelivery drill required'),(65,710,'Fluent Bit','Docker JSON / Nginx / host\nBounded local buffers'),
 (580,710,'OpenSearch','TLS + SigV4 on AWS\n30-day index retention policy')],[(0,1),(1,2),(1,3),(3,4),(0,5),(5,6)])
render('05-security-flow.png','Security controls','Defense across application, delivery, networking and data boundaries',[
 (65,210,'HTTPS entry','ACM certificate / TLS\nHTTP redirect / rate limits'),(580,210,'Authentication','Argon2 passwords / JWT\nRotating refresh tokens'),
 (1095,210,'Authorization','Admin / Engineer / Viewer\nDatabase-backed user status'),(1095,465,'Audit + correlation','Structured JSON / request ID\nMutation and login audit trail'),
 (580,710,'Private data','Security groups / encryption\nRDS TLS and Redis AUTH/TLS'),(65,710,'Release integrity','Immutable digests / scans\nApproval / smoke / rollback')],[(0,1),(1,2),(2,3),(3,4),(5,0),(2,4)])
