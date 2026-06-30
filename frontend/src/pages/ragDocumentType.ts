export const documentTypeOptions = [
  '安防制度',
  '人员档案',
  '摄像头安装说明',
  '访客管理规定',
  '应急处置流程',
] as const;

export type RAGDocumentType = (typeof documentTypeOptions)[number];

interface Rule {
  type: RAGDocumentType;
  keywords: string[];
  hint: string;
}

const rules: Rule[] = [
  {
    type: '应急处置流程',
    keywords: ['事件', '处置', '应急', 'sop', '复盘', '升级', '告警'],
    hint: '命中文件名中的事件、处置、应急或复盘关键词。',
  },
  {
    type: '摄像头安装说明',
    keywords: ['摄像头', 'camera', 'rtsp', '安装', '运维', '离线', '画面', '设备'],
    hint: '命中文件名中的摄像头、设备、安装或运维关键词。',
  },
  {
    type: '访客管理规定',
    keywords: ['访客', '门禁', '通行', '权限', '授权', '登记', '外包'],
    hint: '命中文件名中的访客、门禁、通行或权限关键词。',
  },
  {
    type: '人员档案',
    keywords: ['人员', '员工', '档案', '名单', '部门', '身份'],
    hint: '命中文件名中的人员、员工、档案或名单关键词。',
  },
  {
    type: '安防制度',
    keywords: ['制度', '规范', '值班', '安全', '安防', '规定'],
    hint: '命中文件名中的制度、规范、值班或安防关键词。',
  },
];

export function inferDocumentType(filename: string): { type: RAGDocumentType; reason: string } {
  const normalized = filename.toLowerCase();
  for (const rule of rules) {
    const matchedKeyword = rule.keywords.find((keyword) => normalized.includes(keyword.toLowerCase()));
    if (matchedKeyword) {
      return {
        type: rule.type,
        reason: `${rule.hint}匹配词：“${matchedKeyword}”。`,
      };
    }
  }

  return {
    type: '安防制度',
    reason: '未识别到明确关键词，先归入通用安防制度；你可以手动改成更准确的类型。',
  };
}

export const documentTypeDescriptions: Record<RAGDocumentType, string> = {
  安防制度: '规章制度、值班规范、区域权限、安全要求。',
  人员档案: '员工、访客、部门、身份、人员基础信息。',
  摄像头安装说明: '摄像头点位、RTSP、安装、离线和运维说明。',
  访客管理规定: '访客登记、临时授权、门禁通行和权限规则。',
  应急处置流程: '事件 SOP、告警升级、处置步骤和复盘记录。',
};
